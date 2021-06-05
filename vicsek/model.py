import numpy as np
from scipy.spatial.distance import pdist, squareform
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from functools import wraps
from pathlib import Path
from tqdm.autonotebook import tqdm

#plt.style.use(Path(__file__).resolve().parent / "vicsek.mplstyle")

# Hard-coded interval for updating text overlay on animation and progress bar
# This does not apply to particles which are updated every step
ANI_UPDATE_INTERVAL = 10


def expand_to_array(setter):
    """Decorator for property setters in the VicsekModel class, which takes inputs that
    are numbers or iterables, and expands them into numpy arrays with a length equal to
    the number of agents, by repeating the number or the [-1] element of the iterable.
    """

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
    """
    Class which implements the two-dimensional Vicsek model.

    Inputs:
    -------
    length: int
        Side length of square box.
    density: float
        Number of agents per square unit of the box.
    speed: float or iterable
        Magnitude of the velocity of the agents.
    noise: float or iterable
        Perturbations are drawn from a uniform distribution with limits +/- 0.5*noise.
    radius: float or iterable (optional)
        Interaction radius of agents.
    weights: float or iterable (optional)
        Relative weights of the agents in the interaction. By default they all
        contribute to the interaction with the same weight.

    Notes:
    ------
    The speed, noise, radius and weights can be provided as either a single number or
    an interable of length less than or equal to the number of agents (density
    multiplied by length squared). Inputs will be expanded to an array of the correct
    length by repeating the [-1] element from the input, viewed as an iterable.

    For example:

        >>> VicsekModel(..., radius=[4, 3, 2, 1], ...)

    will be expanded to `numpy.array([4, 3, 2, 1, 1, ..., 1])`
    """

    def __init__(
        self,
        length,
        density,
        speed,
        noise,
        radius=3,
        weights=1,
    ):

        self.length = length
        self.density = density
        self.speed = speed
        self.noise = noise
        self.radius = radius
        self.weights = weights

        self.init_state(reproducible=False)

    # --------------------------------------------------------------------------------
    #                                                             | Data descriptors |
    #                                                             --------------------

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

    # --------------------------------------------------------------------------------
    #                                                         | Read-only properties |
    #                                                         ------------------------

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
    def agents(self):
        """Number of agents (particles) in the simulation."""
        return int(self._density * self.length ** 2)

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

    # --------------------------------------------------------------------------------
    #                                                            | Protected methods |
    #                                                            ---------------------

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

    # --------------------------------------------------------------------------------
    #                                                               | Public methods |
    #                                                               ------------------

    def copy(self):
        """Returns a new object with the same values of the parameters."""
        return VicsekModel(
            length=self.length,
            density=self.density,
            speed=self.speed,
            noise=self.noise,
            radius=self.radius,
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

    def evolve(self, steps: int, track_order_parameter=False, interval=10, pbar=None):
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
                if pbar is not None:
                    pbar.update()

        else:
            for _ in range(steps):
                self._step()
            if pbar is not None:
                pbar.update()

    def evolve_ensemble(self, ensemble_size: int, steps: int):
        """Evolve a number of identical models with different initial conditions.

        Inputs:
        -------
        ensemble_size: int
            Number of replica
        steps: int
            Number of steps to evolve for, aka trajectory length

        Returns:
        --------
        mean: float
            Mean value of the order parameter at the end of the trajectory
        var: float
            Sample variance of the order parameter at the end of the trajectory

        Notes:
        ------
        A more flexible version of this, which allow the trajectories to be
        visualised and the simulations to be resumed (as opposed to restarted)
        if `steps` is understimated, is provided in vicsek.scripts.evolve_ensemble.
        """
        pbar = tqdm(total=(ensemble_size * steps), desc="Completed 0 simulations")
        order_parameters = np.empty(ensemble_size)
        for i in range(ensemble_size):
            self.init_state(reproducible=False)
            self.evolve(steps, track_order_parameter=False, pbar=pbar)
            pbar.set_description(f"Completed {i} simulations")
            pbar.refresh()
            order_parameters[i] = self.order_parameter
        pbar.close()

        return order_parameters.mean(), order_parameters.var(ddof=1)

    # --------------------------------------------------------------------------------
    #                                                                | Visualisation |
    #                                                                -----------------

    def get_box(self):
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

    def plot_state(self, outpath=None):
        """Plot the current state of the system using quivers."""
        fig, ax = self.get_box()

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
    ):
        """Animation of the agent positions.

        Inputs:
        -------
        steps: int
            Number of steps to evolve for.
        outpath: str (optional)
            Path to directory where animation will be saved.
        anneal: bool (optional)
            If True, the noise magnitude throughout the simulation will vary from a
            maximum of 2\pi and a minimum of 0.
        anneal_periods: int (optional)
            Number of full oscillation periods of the noise. For traditional annealing
            set equal to 0.5.
        """

        fig, ax = self.get_box()

        # Set disc radii equal to half their interaction radii
        # NOTE: if all radii are the same this looks good, but misleading if they
        # vary. Without factor of half it looks too big though, in my opinion
        pixel_density = (
            ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted()).width
            * fig.dpi
            / self.length
        )
        disc_sizes = (0.5 * pixel_density * self.radius) ** 2

        agents = ax.scatter(
            self.positions[:, 0],
            self.positions[:, 1],
            s=disc_sizes,
            c=self.weights,
            cmap="viridis_r",
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
                f"$\eta$ = {(2 * np.pi):1.1f}",
                xy=(0.78, 0.9),
                xycoords="axes fraction",
                zorder=2,
                fontsize=12,
            )
            omega = 2 * np.pi * anneal_periods / steps

        pbar = tqdm(total=steps, desc="Steps completed")

        def basic_loop(t):
            self._step()
            agents.set_offsets(self.positions)
            if t % ANI_UPDATE_INTERVAL == 0:
                op_label.set_text(f"V = {self.order_parameter:1.2f}")
                pbar.update(ANI_UPDATE_INTERVAL)
            return (agents, op_label)

        def annealing_loop(t):
            (agents, op_label) = basic_loop(t)
            if t % ANI_UPDATE_INTERVAL == 0:
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
        pbar.close()

        return ani
