from vicsek.model import VicsekModel
from vicsek.visualize import ParticlesAnimation


def test_animation_runs():
    model = VicsekModel(10, 1, speed=1, noise=1)
    animator = ParticlesAnimation(model)

    _ = animator.animate(frames=10)
