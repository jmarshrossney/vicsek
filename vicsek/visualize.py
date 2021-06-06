from collections.abc import Iterable
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
import numpy as np

# TODO set default style but allow easy overriding
plt.style.use("vicsek.mplstyle")


def get_pixel_density(model) -> float:
    """Returns the number of pixels per unit *length* on a standard figure.

    Useful if you want the size of the particles in the animation to correspond
    to a 'physical' length scale such as the interaction radius.

    For example:

        >>> rho = get_pixel_density(model)
        >>> sizes = (rho * model.radius) ** 2
        >>> animation = ParticlesAnimation(model, sizes=sizes)

    """
    fig, ax = plt.subplots()
    return (
        fig.gca().get_window_extent().transformed(fig.dpi_scale_trans.inverted()).width
        * fig.dpi
        / model.length
    )


class ParticlesAnimation:
    """
    Class which animates the particles for a provided model.

    Parameters
    ----------
    model : VicsekModel
        The model whose particles will be animated by repeatedly calling its
        ``step()`` method.
    sizes : float, iterable or None, optional
        Sizes of the particles in the animation. Default, None.
    colors : colour, iterable or None
        Colour of the particles. Default, None.

    Notes
    -----
    The appearance of the animation can be controlled by specifying parameters in
    vicsek.mplstyle. E.g. when ``sizes`` is None the size is controlled by
    ``rcParams['lines.markersize'] ** 2``. See docs for matplotlib.pyplot.scatter.
    """

    def __init__(self, model, *, sizes=None, colors=None):
        self.model = model
        self.sizes = sizes
        self.colors = colors

    def animation_init(self):
        """Initialises the figure with any non-animated components.

        In this case we simply remove the axes and add a square box patch.
        """
        fig, ax = plt.subplots()

        # Hide axes and make figure square (L, L)
        ax.set_axis_off()
        ax.set_aspect("equal")

        # Add a box
        box = Rectangle(
            xy=(0, 0),
            width=self.model.length,
            height=self.model.length,
            edgecolor="black",
            facecolor="none",
            linewidth=2,
        )
        ax.add_patch(box)

        return fig

    def add_artists(self, fig):
        """Adds the artists (components) to be animated.

        In this case we simply add the particles.
        """
        particles = fig.gca().scatter(
            self.model.positions[:, 0],
            self.model.positions[:, 1],
            s=self.sizes,
            c=self.colors,
        )
        return (particles,)

    def loop(self, t: int, artists) -> tuple:
        """The function to be iterated over by the animation.

        Takes a frame number ``t`` and the PathCollection object returned by
        ``matplotlib.pyplot.scatter`` containing the current snapshot of the
        particles. Applies ``self.model.step()`` and then updates the coordinates
        of the particles.
        """
        self.model.step()
        (particles,) = artists
        particles.set_offsets(self.model.positions)
        return (particles,)

    def animate(self, steps: int = 100, interval: int = 30) -> FuncAnimation:
        """Returns the animation.

        Parameters
        ----------
        steps : int, optional
            Number of times the model is stepped forward during the animation.
            Also the number of frames in the animation. 100 by default.
        interval : int, optional
            Time in ms between frames. 30ms by default.

        Returns
        -------
        FuncAnimation

        Notes
        -----
        It is not necessary to specify ``steps`` if one is just viewing the
        animation using ``plt.show()``.

        To save the animation, use ``ani.save('animation.gif')``.
        """
        fig = self.animation_init()

        artists = self.add_artists(fig)

        def _loop(t):
            return self.loop(t, artists)

        ani = FuncAnimation(fig, _loop, frames=steps, interval=interval, blit=True)

        return ani


class ParticlesAnimationWithAnnealing(ParticlesAnimation):
    """Example of an extension to ``ParticlesAnimation``.

    Here we anneal the noise parameter from 2pi to 0 during the animation, and
    also display the current noise and current order parameter. Note that this
    overrides whatever ``model.noise`` is set to.

    Parameters
    ----------
    model : VicsekModel
        The model whose particles will be animated by repeatedly calling its
        ``step()`` method.
    anneal_period : int, optional
        Number of steps over which the noise will complete a full oscillation
        from a 2pi -> 0 -> 2pi. By default, 200.
        which is standard annealing behaviour (max noise -> min noise -> stop).
    sizes : float, iterable or None, optional
        Sizes of the particles in the animation. Default, None.
    colors : colour, iterable or None
        Colour of the particles. Default, None.

    """

    def __init__(
        self,
        model,
        *,
        anneal_period: float = 200,
        sizes=None,
        colors=None,
    ):
        super().__init__(model, sizes=sizes, colors=colors)
        self.anneal_period = anneal_period

    def add_artists(self, fig):
        """Extends super().add_artists() to add annotations for the noise and the
        order parameter."""
        (particles,) = super().add_artists(fig)
        op_label = fig.gca().annotate(
            f"OP = {self.model.order_parameter:1.2f}",
            xy=(0.06, 0.9),
            xycoords="axes fraction",
            fontsize=12,
        )
        noise_label = fig.gca().annotate(
            f"$\eta$ = {(2 * np.pi):1.1f}",
            xy=(0.78, 0.9),
            xycoords="axes fraction",
            fontsize=12,
        )
        return (particles, op_label, noise_label)

    def loop(self, t, artists):
        """Extends super().loop() to also vary the noise during the animation, and
        add annotations for the noise and the order parameter."""
        particles, op_label, noise_label = artists
        super().loop(t, particles)

        current_noise = np.pi * (1 + np.cos(2 * np.pi * t / self.anneal_period))
        self.model.noise = np.full(self.model.particles, fill_value=current_noise)

        op_label.set_text(f"OP = {self.model.order_parameter:1.2f}")
        noise_label.set_text(f"$\eta$ = {current_noise:1.1f}")
        return artists
