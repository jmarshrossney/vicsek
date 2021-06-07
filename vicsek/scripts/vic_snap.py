from pathlib import Path

import matplotlib.pyplot as plt
from tqdm.autonotebook import tqdm

from vicsek.config import parser
from vicsek.model import VicsekModel

parser.add("--frames", type=int, default=100, help="number of snapshots to save")
parser.add("--steps", type=int, default=1, help="number of steps between snapshots")


def main():
    args = parser.parse_args()

    outpath = Path(args.outpath) / "snapshots"

    # Really don't want to mix output with snaps from a previous simulation...
    assert not outpath.is_dir(), f"Existing directory at {outpath.resolve()}."

    outpath.mkdir(parents=True)

    model = VicsekModel(
        length=args.length,
        density=args.density,
        speed=args.speed,
        noise=args.noise,
        radius=args.radius,
        weights=args.weights,
        seed=args.seed,
    )
    n = len(str(args.steps * args.frames))

    # Save initial config
    fig = model.view()
    fig.savefig(outpath / f"snap_{str(0).zfill(n)}.png")
    plt.close(fig)

    pbar = tqdm(range(args.frames))
    for i in pbar:
        model.evolve(steps=args.steps)
        fig = model.view()
        fig.savefig(outpath / f"snap_{str(model.current_step).zfill(n)}.png")
        plt.close(fig)

    pbar.close()


if __name__ == "__main__":
    main()
