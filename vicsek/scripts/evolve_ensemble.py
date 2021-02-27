import numpy as np
import matplotlib.pyplot as plt
from tqdm.autonotebook import tqdm
from pathlib import Path


def save_fig(fig, outpath):
    outpath = Path(outpath)
    outpath.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath / "ensemble.png")


def evolve_ensemble(
    model, ensemble_size, steps, interval=10, outpath=None, interactive=False
):

    ensemble = [model.copy() for _ in range(ensemble_size)]

    finished = False
    while not finished:
        fig, ax = plt.subplots()
        ax.set_xlabel("steps")
        ax.set_ylabel("order parameter")

        pbar = tqdm(total=ensemble_size, desc="Simulations completed")

        for replica in ensemble:

            replica.evolve(steps, track_order_parameter=True, interval=interval)

            # NOTE: dict not ordered so should strictly sort, but so far never needed
            # pairs = sorted(replica.trajectory.items())
            ax.plot(replica.trajectory.keys(), replica.trajectory.values())

            pbar.update()

        pbar.close()

        if not interactive:
            if outpath is not None:
                save_fig(fig, outpath)
            break

        plt.show()

        instruct = input("Continue? (y/n) > ")
        if "y" in instruct.lower():
            steps = int(
                input("How many more steps to evolve for? (enter an integer) > ")
            )
            interval = int(
                input(
                    "How many steps between order parameter measurements? (enter an integer) > "
                )
            )
        else:
            if outpath is not None:
                save_fig(fig, outpath)
            finished = True
