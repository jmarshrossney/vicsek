import numpy as np
from timeit import timeit

from vicsek.model import VicsekModel
from vicsek.config import parser
from vicsek.scripts.evolve_ensemble import evolve_ensemble

ARGS = parser.parse_args()


def load_model():
    """Returns loaded model."""
    model = VicsekModel(
        length=ARGS.length,
        density=ARGS.density,
        speed=ARGS.speed,
        radius=ARGS.radius,
        noise=ARGS.noise,
        weights=ARGS.weights,
    )
    model.init_state(reproducible=ARGS.reproducible)

    return model


MODEL = load_model()


def anim():

    MODEL.animate(
        steps=ARGS.steps,
        outpath=ARGS.outpath,
        anneal=ARGS.anneal,
        anneal_periods=ARGS.anneal_periods,
        anneal_interval=ARGS.anneal_interval,
        cmap=ARGS.cmap,
    )


def time():

    t = timeit(
        stmt="MODEL.evolve(steps=ARGS.steps)",
        number=ARGS.repeats,
        globals=globals(),
    )
    print(
        f"""
        Number of agents:       {MODEL.agents}
        Simulation length:      {ARGS.steps} steps
        Number of simulations:  {ARGS.repeats}
        Time taken:             {t:.4g} seconds
        """
    )


def evol():

    evolve_ensemble(
        MODEL,
        ensemble_size=ARGS.ensemble_size,
        steps=ARGS.steps,
        interval=ARGS.op_interval,
        outpath=ARGS.outpath,
        interactive=ARGS.interactive,
    )

    pass