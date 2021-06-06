from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from tqdm.autonotebook import tqdm


def save_fig(fig, outpath):
    outpath = Path(outpath)
    outpath.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath / "ensemble.png")


def evolve_ensemble(ensemble: list, steps: int, outpath: Path, snapshot_interval: int):

    fig, ax = plt.subplots()
    ax.set_xlabel("steps")
    ax.set_ylabel("order parameter")

    pbar = tqdm(total=(steps * ensemble_size), desc="Completed 0 simulations")

    for i, replica in enumerate(ensemble):

        replica.evolve(steps, track_order_parameter=True, pbar=pbar)

        pbar.set_description(f"Completed {i} simulations")
        pbar.refresh()

        # NOTE: dict not ordered so should strictly sort, but so far never needed
        # pairs = sorted(replica.trajectory.items())
        ax.plot(replica.trajectory.keys(), replica.trajectory.values())

    pbar.close()

