import logging
from pathlib import Path

import matplotlib.pyplot as plt

from vicsek.config import parser
from vicsek.model import VicsekModel
from vicsek.style import default_animation_style
from vicsek.visualize import ParticlesAnimation

log = logging.getLogger(__name__)

parser.add("--frames", type=int, default=100, help="number of frames in the animation")
parser.add("--steps", type=int, default=1, help="number of steps per frame")
parser.add("--interval", type=int, default=30, help="number of ms between frames")

plt.style.use(default_animation_style)

FNAME = "animation.gif"


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

    model = VicsekModel(
        length=args.length,
        density=args.density,
        speed=args.speed,
        noise=args.noise,
        radius=args.radius,
        weights=args.weights,
        seed=args.seed,
    )

    animator = ParticlesAnimation(model)
    animation = animator.animate(
        frames=args.frames,
        steps=args.steps,
        interval=args.interval,
    )
    animation.save(outpath / FNAME)


if __name__ == "__main__":
    main()
