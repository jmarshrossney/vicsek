from collections.abc import Iterable
from functools import wraps
import logging
from typing import Union

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from scipy.spatial.distance import pdist, squareform

log = logging.getLogger(__name__)

ParticleProperty = Union[float, Iterable[float]]


# TODO: probably silly to rely on explicit property 'particles'
def expand_to_array(setter):
    """Decorator for property setters which which takes inputs that are either numbers
    or iterables, and expands them into numpy arrays with a length equal to the number
    of particles, by repeating the number or the [-1] element of the iterable.

    Raises
    ------
    ValueError
        If the input iterable has more elements than the number of particles.

    """

    @wraps(setter)
    def wrapper(instance, new):
        if not hasattr(new, "__iter__"):
            new = [new]
        if len(new) > instance.particles:
            raise ValueError(
                "Too many values provided in setter: {setter}. Expected {instance.particles} but got {len(new)}"
            )
        array = np.full(instance.particles, fill_value=new[-1], dtype=np.float64)
        array[: len(new)] = new
        array = np.flip(array)  # means 'special' ones are plotted above others
        setter(instance, array)

    return wrapper


class VicsekModel:
    """
    Class which implements the two-dimensional Vicsek model.

    The original model was introduced by Vicsek et al, Phys. Rev. Lett. 75 (1995).

    Parameters
    ----------
    length : int
        Side length of square box.
    density : float
        Number of particles per square unit of the box.
    speed : float or iterable
        Magnitude of the velocity of the particles.
    noise : float or iterable
        Magnitude of the noise perturbation. Perturbations are drawn from a uniform
        distribution with limits +/- ``0.5*noise``.
    radius : float or iterable, optional
        Interaction radius of particles. One by default.
    weights : float or iterable, optional
        Relative weights of the particles in the interaction term. By default all
        particles carry the same weight.
    seed : int or None, optional
        Seed for random number generator. By providing a known integer one can
        reproduce the evolution of the model. None by default.

    Notes
    -----
    The speed, noise, radius and weights can be provided as either a single number
    or an iterable of length less than or equal to the number of particles in the
    system. Inputs will be expanded to an array of the correct length by repeating
    the [-1] element, using ``expand_to_array``.

    For example:

        >>> model = VicsekModel(6, 1, 1, noise=[4, 2, 3, 1])
        >>> model.noise
        array([1., 1., 1., ... 1., 3., 2., 4.])
        >>> model.noise.size
        36

    The reason that the elements appear in reverse order is so that the 'interesting'
    particles appear on top if the model is animated.

    """

    def __init__(
        self,
        length: int,
        density: float,
        speed: ParticleProperty,
        noise: ParticleProperty,
        radius: ParticleProperty = 1,
        weights: ParticleProperty = 1,
        seed: Union[int, None] = None,
    ):

        self.length = length
        self.density = density
        self.speed = speed
        self.noise = noise
        self.radius = radius
        self.weights = weights

        self.init_state(seed=seed)

    # --------------------------------------------------------------------------------
    #                                                             | Data descriptors |
    #                                                             --------------------

    @property
    def length(self) -> int:
        """Side length of the square box containing the system."""
        return self._length

    @length.setter
    def length(self, new: int):
        """Setter for length. Also reinitialises state."""
        self._length = new
        if hasattr(self, "_reset_flag"):
            log.info("Resetting model to random initial configuration")
            self.init_state()

    @property
    def density(self) -> float:
        """Number density of particles in the box."""
        return self._density

    @density.setter
    def density(self, new: float):
        """Setter for density. Also reinitialises state."""
        self._density = new
        if hasattr(self, "_reset_flag"):
            log.info("Resetting model to random initial configuration")
            self.init_state()

    @property
    def speed(self) -> np.ndarray:
        """Magnitude of the velocity of the particles. Since the time-step is set equal to
        one, this is also the distance travelled in one update."""
        return self._speed

    @speed.setter
    @expand_to_array
    def speed(self, new: ParticleProperty):
        """Setter for speed."""
        self._speed = new

    @property
    def radius(self) -> np.ndarray:
        """Radius of interaction. Agents that are closer than this length will exert
        an influence on each other's headings."""
        return self._radius

    @radius.setter
    @expand_to_array
    def radius(self, new: ParticleProperty):
        """Setter for radius."""
        self._radius = new

    @property
    def noise(self) -> np.ndarray:
        """Magnitude of the random scalar noise that perturbs the heading."""
        return self._noise

    @noise.setter
    @expand_to_array
    def noise(self, new: ParticleProperty):
        """Setter for noise."""
        self._noise = new

    @property
    def weights(self) -> np.ndarray:
        """Array containing the relative weights of the particles, which determines how
        influencial they are in determining the heading of nearby particles."""
        return self._weights

    @weights.setter
    @expand_to_array
    def weights(self, new: ParticleProperty):
        """Setter for weights."""
        if np.any(new < 0):
            raise ValueError("The weights must be positive.")
        self._weights = new

    # --------------------------------------------------------------------------------
    #                                                         | Read-only properties |
    #                                                         ------------------------

    @property
    def positions(self) -> np.ndarray:
        """Array of shape (particles, 2) containing the x and y coordinates of the
        particles."""
        return self._positions

    @property
    def headings(self) -> np.ndarray:
        """Array containing the headings (polar angle) of the particles."""
        return self._headings

    @property
    def velocities(self) -> np.ndarray:
        """Array of shape (particles, 2) containing the x and y components of the
        velocities of the particles."""
        return np.expand_dims(self.speed, 1) * np.stack(
            (np.cos(self.headings), np.sin(self.headings)), axis=1
        )

    @property
    def particles(self) -> int:
        """Number of particles in the simulation."""
        return int(self._density * self.length ** 2)

    @property
    def order_parameter(self) -> float:
        """Magnitude of the combined velocity of all particles, normalised to [0, 1]."""
        return (
            np.sqrt(np.square(self.velocities.mean(axis=0)).sum()) / self.speed.mean()
        )

    @property
    def current_step(self) -> int:
        """Number of steps taken since the model was initialised."""
        return self._current_step

    @property
    def trajectory(self) -> dict:
        """A dictionary describing the trajectory of the order parameter (values) in
        terms of the number of steps since initialisation (keys)."""
        # NOTE: I removed the flexibility to measure OP every X steps, so the dict
        # constructions is not necessary.
        return self._trajectory

    # --------------------------------------------------------------------------------
    #                                                               | Public methods |
    #                                                               ------------------

    def init_state(self, seed: Union[int, None] = None):
        """Initialises the model by randomly generating positions and headings.

        Parameters
        ----------
        seed : int or None
            Seed for random number generator. By providing a known integer one can
            reproduce the evolution of the model.
        """
        self._rng = np.random.default_rng(seed)

        self._positions = self._rng.random((self.particles, 2)) * self.length
        self._headings = self._rng.random(size=self.particles) * 2 * np.pi

        self._current_step = 0
        self._trajectory = {0: self.order_parameter}

        self._reset_flag = True

    def step(self):
        """Performs a single step for all particles."""
        # Generate adjacency matrix - true if separation less than radius
        distance_matrix = squareform(pdist(self.positions))
        adjacency_matrix = distance_matrix < self.radius

        # Average over current headings of particles within radius
        headings_matrix = np.ma.array(
            np.broadcast_to(self.headings, (self.particles, self.particles)),
            mask=~adjacency_matrix,
        )
        sum_of_sines = (self.weights * np.sin(headings_matrix)).sum(axis=1)
        sum_of_cosines = (self.weights * np.cos(headings_matrix)).sum(axis=1)

        # Set new headings
        self._headings = (
            np.arctan2(sum_of_sines, sum_of_cosines)  # interactions
            + (self._rng.random(self.particles) - 0.5) * self.noise  # noise
        )

        # Step forward particles
        self._positions += np.expand_dims(self.speed, 1) * np.stack(
            (np.cos(self.headings), np.sin(self.headings)),
            axis=1,
        )

        # Check for wrapping around the periodic boundaries
        np.mod(self._positions, self.length, out=self._positions)

        # Update step counter
        self._current_step += 1

    def evolve(
        self,
        steps: int,
        track_order_parameter: bool = False,
    ):
        """Evolves the system forwards a number of steps.

        Parameters
        ----------
        steps : int
            Number of updates.
        track_order_parameter : bool, optional
            If True, update the trajectory of the order parameter during evolution.
            False by default.
        """
        for _ in range(steps):
            self.step()
            if track_order_parameter:
                self._trajectory[self.current_step] = self.order_parameter

    def get_box(self) -> Rectangle:
        """Returns a Rectangle patch representing the box."""
        return Rectangle(
            xy=(0, 0),
            width=self.length,
            height=self.length,
            edgecolor="black",
            facecolor="none",
            linewidth=2,
        )

    def view(self, annotate=True) -> plt.figure:
        """Visualise the current state of the system using quivers.

        Parameters
        ----------
        annotate : bool, optional
            If True, annotate the plot with the current value of the order
            parameter and the number of steps since the model was initialised.
            True by default.

        Returns
        -------
        matplotlib.pyplot.figure
        """
        fig, ax = plt.subplots()

        # Hide axes and make figure square (L, L)
        ax.set_axis_off()
        ax.set_aspect("equal")

        # Add a box
        box = self.get_box()
        ax.add_patch(box)

        ax.quiver(
            self.positions[:, 0],
            self.positions[:, 1],
            self.velocities[:, 0],
            self.velocities[:, 1],
        )
        if annotate:
            ax.annotate(
                f"OP = {self.order_parameter:1.2f}",
                xy=(0.9, -0.1),
                xycoords="axes fraction",
                fontsize=12,
            )
            ax.annotate(
                f"t = {self.current_step}",
                xy=(0, -0.1),
                xycoords="axes fraction",
                fontsize=12,
            )
        return fig
