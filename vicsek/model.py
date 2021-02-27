import numpy as np
from scipy.spatial.distance import pdist, squareform
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from functools import wraps
from pathlib import Path


def expand_to_array(setter):
    @wraps(setter)
    def wrapper(instance, new):
        if not hasattr(new, "__iter__"):
            new = [new]
        if len(new) > instance.agents:
            raise ValueError(
                "Too many values provided in setter: {setter}. Expected {instance.agents} but got {len(new)}"
            )
        array = np.full(instance.agents, fill_value=new[-1], dtype=np.float64)
        array[: len(new)] = new
        array = np.flip(array)  # means 'special' ones are plotted above others
        setter(instance, array)

    return wrapper


class VicsekModel:
    def __init__(
        self,
        length: int,
        density: float,
        speed: float,
        radius: float,
        noise: float,
        weights: float = 1,
    ):

        self.length = length
        self.density = density
        self.speed = speed
        self.radius = radius
        self.noise = noise
        self.weights = weights

        self.init_state(reproducible=False)

    @property
    def agents(self):
        """Number of agents (particles) in the simulation."""
        return self._agents

    @property
    def positions(self):
        """Array of shape (agents, 2) containing the x and y coordinates of the
        agents."""
        return self._positions

    @property
    def headings(self):
        """Array containing the headings (polar angle) of the agents."""
        return self._headings

    @property
    def velocities(self):
        """Array of shape (agents, 2) containing the x and y components of the
        velocities of the agents."""
        return np.expand_dims(self.speed, 1) * np.stack(
            (np.cos(self.headings), np.sin(self.headings)), axis=1
        )

    @property
    def order_parameter(self):
        """Magnitude of the combined velocity of all agents, normalised to [0, 1]."""
        return (
            np.sqrt(np.square(self.velocities.mean(axis=0)).sum()) / self.speed.mean()
        )

    @property
    def current_step(self):
        """Number of steps taken since the model was initialised."""
        return self._current_step

    @property
    def trajectory(self):
        """A dictionary describing the trajectory of the order parameter (values) in
        terms of the number of steps since initialisation (keys)."""
        return self._trajectory

    # -----------------------

    @property
    def length(self):
        """Side length of the square box containing the system."""
        return self._length

    @length.setter
    def length(self, new_value):
        """Setter for length. Also reinitialises state."""
        if not isinstance(new_value, (int, float)):
            raise TypeError(
                "Please provide an integer or float for the length of the box."
            )
        if new_value <= 0:
            raise ValueError("Please enter a positive, nonzero length for the box.")
        self._length = new_value
        if hasattr(self, "_reset_flag"):
            print("Resetting model to random initial configuration")
            self.init_state()

    @property
    def density(self):
        """Number density of agents in the box."""
        return self._density

    @density.setter
    def density(self, new_value):
        """Setter for density. Also reinitialises state."""
        if new_value < 0 or new_value > 1:
            raise ValueError("Please provide a density between 0 and 1.")
        self._density = new_value
        self._agents = int(
            self._density * self.length ** 2
        )  # NOTE: must set length first!
        if hasattr(self, "_reset_flag"):
            print("Resetting model to random initial configuration")
            self.init_state()

    @property
    def speed(self):
        """Magnitude of the velocity of the agents. Since the time-step is set equal to
        one, this is also the distance travelled in one update."""
        return self._speed

    @speed.setter
    @expand_to_array
    def speed(self, new):
        """Setter for speed."""
        if np.any(new < 0):
            raise ValueError("The speed must be positive.")
        self._speed = new

    @property
    def radius(self):
        """Radius of interaction. Agents that are closer than this length will exert
        an influence on each other's headings."""
        return self._radius

    @radius.setter
    @expand_to_array
    def radius(self, new):
        """Setter for radius."""
        if np.any(new < 0):
            raise ValueError("The interaction radius must be positive.")
        self._radius = new

    @property
    def noise(self):
        """Magnitude of the random scalar noise that perturbs the heading."""
        return self._noise

    @noise.setter
    @expand_to_array
    def noise(self, new):
        if np.any(new < 0):
            raise ValueError("The noise magnitude must be positive.")
        self._noise = new

    @property
    def weights(self):
        """Array containing the relative weights of the agents, which determines how
        influencial they are in determining the heading of nearby agents."""
        return self._weights

    @weights.setter
    @expand_to_array
    def weights(self, new):
        """Setter for weights."""
        if np.any(new < 0):
            raise ValueError("The weights must be positive.")
        self._weights = new

    # ------------------------

    def _seed_rng(self, seed=None):
        """Resets the random number generator with a seed, for reproducibility. If no
        seed is provided the rng will be randomly re-initialised."""
        self._rng = np.random.default_rng(seed)

    def _step(self):
        """Performs a single step for all agents."""
        # Generate adjacency matrix - true if separation less than radius
        distance_matrix = squareform(pdist(self.positions))
        adjacency_matrix = distance_matrix < self.radius

        # Average over current headings of agents within radius
        headings_matrix = np.ma.array(
            np.broadcast_to(self.headings, (self.agents, self.agents)),
            mask=~adjacency_matrix,
        )
        sum_of_sines = (self.weights * np.sin(headings_matrix)).sum(axis=1)
        sum_of_cosines = (self.weights * np.cos(headings_matrix)).sum(axis=1)

        # Set new headings
        self._headings = (
            np.arctan2(sum_of_sines, sum_of_cosines)  # interactions
            + (self._rng.random(self.agents) - 0.5) * self.noise  # noise
        )

        # Step forward agents
        self._positions += np.expand_dims(self.speed, 1) * np.stack(
            (np.cos(self.headings), np.sin(self.headings)),
            axis=1,
        )

        # Check for wrapping around the periodic boundaries
        np.mod(self._positions, self.length, out=self._positions)

        # Update step counter
        self._current_step += 1

    # -------------------------

    def copy(self):
        """Returns a new object with the same values of the parameters."""
        return VicsekModel(
            length=self.length,
            density=self.density,
            speed=self.speed,
            radius=self.radius,
            noise=self.noise,
            weights=self.weights,
        )

    def init_state(self, reproducible=False):
        """Initialises the model by randomly generating the positions and headings of
        the agents.

        Inputs
        ------
        reproducible: bool (optional)
            If True, the random number generator is initialised with a known seed and
            the simulation can be reproduced exactly with this seed.
        """
        if reproducible:
            self._seed_rng(seed=123456)
        else:
            self._seed_rng(seed=None)

        self._positions = self._rng.random((self.agents, 2)) * self.length
        self._headings = self._rng.random(size=self.agents) * 2 * np.pi

        self._current_step = 0
        self._trajectory = {0: self.order_parameter}

        self._reset_flag = True

    def evolve(self, steps: int, track_order_parameter=False, interval=10):
        """Evolves the system forwards.

        Inputs
        ------
        steps: int
            Number of updates.
        track_order_parameter: bool (optional)
            If True, update the trajectory of the order parameter during evolution.
        interval: int (optional)
            Interval for computing the order parameter.
        """
        if type(steps) is not int:
            raise TypeError("Please provide an integer for the number of steps.")
        if steps < 1:
            raise ValueError("Please enter a positive, nonzero number of steps.")

        if track_order_parameter:
            for _ in range(steps):
                self._step()
                if self.current_step % interval == 0:
                    self._trajectory[self.current_step] = self.order_parameter

        else:
            for _ in range(steps):
                self._step()

    def evolve_ensemble(self, ensemble_size: int, steps: int):
        # NOTE: probably better implemented as an interactive script, allowing
        # user to continue evolution if they underestimated num steps

        # ensemble = [self.copy() for _ in range(ensemble_size)]
        raise NotImplementedError

    # -----------------------

    def _get_box(self):
        """Returns a figure and axis with a box patch, reading for adding agents to
        the plot."""
        fig, ax = plt.subplots()
        ax.set_axis_off()
        ax.set_aspect("equal")

        box = Rectangle(
            xy=(0, 0),
            width=self.length,
            height=self.length,
            edgecolor="black",
            facecolor="none",
            linewidth=2,
        )
        ax.add_patch(box)

        return fig, ax

    def _pixel_density(self, fig, ax):
        """Returns number of pixels per unit length along the box axes."""
        bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        length_in_pixels = bbox.width * fig.dpi
        return length_in_pixels / self.length

    def plot_state(self, outpath=None):
        """Plot the current state of the system using quivers."""
        fig, ax = self._get_box()

        ax.quiver(
            self.positions[:, 0],
            self.positions[:, 1],
            self.velocities[:, 0],
            self.velocities[:, 1],
        )
        ax.annotate(
            f"V = {self.order_parameter:.2g}", xy=(0.9, -0.1), xycoords="axes fraction"
        )

        if outpath is not None:
            outpath = Path(outpath)
            outpath.mkdir(parents=True, exist_ok=True)
            ani.save(outpath / "state.png")

        return fig

    def animate(
        self,
        steps,
        outpath=None,
        anneal=False,
        anneal_periods=1,
        anneal_interval=10,
        cmap="viridis_r",
    ):
        """Animation of the agent positions."""

        fig, ax = self._get_box()

        # Set disc radii equal to half their interaction radii
        # NOTE: if all radii are the same this looks good, but misleading if they
        # vary. Setting equal to radis looks too big though, in my opinion
        pixel_density = self._pixel_density(fig, ax)
        disc_sizes = (0.5 * pixel_density * self.radius) ** 2

        agents = ax.scatter(
            self.positions[:, 0],
            self.positions[:, 1],
            s=disc_sizes,
            c=self.weights,
            cmap=cmap,
            edgecolors="k",
            linewidth=0.5,
            alpha=0.8,
            zorder=1,
        )
        op_label = ax.annotate(
            f"V = {self.order_parameter:.2g}",
            xy=(0.06, 0.9),
            xycoords="axes fraction",
            zorder=2,
            fontsize=12,
        )
        if anneal:
            noise_label = ax.annotate(
                f"$\eta$ = {self.noise[-1]:1.1f}",
                xy=(0.78, 0.9),
                xycoords="axes fraction",
                zorder=2,
                fontsize=12,
            )
            omega = 2 * np.pi * anneal_periods / steps

        def basic_loop(t):
            self._step()
            agents.set_offsets(self.positions)
            op_label.set_text(f"V = {self.order_parameter:.2g}")
            return (agents, op_label)

        def annealing_loop(t):
            (agents, op_label) = basic_loop(t)
            if t % anneal_interval == 0:
                current_noise = np.pi * (1 + np.cos(omega * t))
                self._noise = np.full(self.agents, fill_value=current_noise)
                noise_label.set_text(f"$\eta$ = {current_noise:1.1f}")
            return agents, op_label, noise_label

        if anneal:
            loop = annealing_loop
        else:
            loop = basic_loop

        ani = mpl.animation.FuncAnimation(
            fig, loop, frames=steps, interval=30, blit=True
        )

        if outpath is not None:
            outpath = Path(outpath)
            outpath.mkdir(parents=True, exist_ok=True)
            ani.save(outpath / "animation.gif")

        return ani
