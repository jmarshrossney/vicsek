import logging
from pathlib import Path

import matplotlib.pyplot as plt
from tqdm.autonotebook import tqdm

from vicsek.config import parser
from vicsek.model import VicsekModel

log = logging.getLogger(__name__)

parser.add(
    "--ensemble-size",
    type=int,
    default=10,
    help="number of replica systems to simulate",
)

FNAME = "ensemble.png"


def main():
    args = parser.parse_args()

    outpath = Path(args.outpath)
    if Path(outpath / FNAME).is_file():
        log.warning(
            f"Existing animation found at '{outpath.resolve()}/{FNAME}'. This will be overwritten."
        )
    if not Path(outpath).is_dir():
        outpath.mkdir(parents=True)

    if args.style is not None:
        plt.style.use(args.style)

    ensemble = [
        VicsekModel(
            length=args.length,
            density=args.density,
            speed=args.speed,
            noise=args.noise,
            radius=args.radius,
            weights=args.weights,
            seed=args.seed,
        )
        for _ in range(args.ensemble_size)
    ]

    steps = 100
    finished = False
    while not finished:
        pbar = tqdm(total=len(ensemble), desc="Completed 0 simulations")

        for i, replica in enumerate(ensemble):

            replica.evolve(steps, track_order_parameter=True)

            pbar.set_description(f"Completed {i + 1} simulations")
            pbar.update()

        pbar.close()

        fig, ax = plt.subplots()
        ax.set_xlabel("Steps")
        ax.set_ylabel("Order Parameter")
        for replica in ensemble:
            ax.plot(replica.trajectory.keys(), replica.trajectory.values())

        plt.show()

        instruct = input("Continue? (y/n) > ")
        if "y" in instruct.lower():
            steps = int(
                input("How many more steps to evolve for? (enter an integer) > ")
            )
        else:
            finished = True

    fig.savefig(outpath / FNAME)


if __name__ == "__main__":
    main()
