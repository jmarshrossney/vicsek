from pathlib import Path

import matplotlib.pyplot as plt
from tqdm.autonotebook import tqdm

from vicsek.config import parser
from vicsek.model import VicsekModel
from vicsek.visualize import snapshot


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
    fig = snapshot(model, 0)
    fig.savefig(outpath / f"snap_{str(0).zfill(n)}.png")
    plt.close(fig)

    pbar = tqdm(range(args.frames))
    for i in pbar:
        model.evolve(steps=args.steps)
        t = i * args.steps
        fig = snapshot(model, t)
        fig.savefig(outpath / f"snap_{str(t).zfill(n)}.png")
        plt.close(fig)

    pbar.close()


if __name__ == "__main__":
    main()
