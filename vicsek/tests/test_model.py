import numpy as np
import pytest

from vicsek.model import VicsekModel


def _test_correct_n_particles(model):
    assert model.speed.size == model.particles
    assert model.noise.size == model.particles
    assert model.radius.size == model.particles
    assert model.weights.size == model.particles


def test_numeric_input():
    model = VicsekModel(10, 1, speed=1, noise=1, radius=1, weights=1)
    _test_correct_n_particles(model)


def test_tuple_input():
    model = VicsekModel(
        10,
        1,
        speed=(1,),
        noise=(1, 1),
        radius=(1, 1, 1, 1),
        weights=tuple([1 for _ in range(100)]),
    )
    _test_correct_n_particles(model)


def test_list_input():
    model = VicsekModel(
        10,
        1,
        speed=[1],
        noise=[1, 1],
        radius=[1, 1, 1, 1],
        weights=[1 for _ in range(100)],
    )
    _test_correct_n_particles(model)


def test_array_input():
    model = VicsekModel(
        10,
        1,
        speed=np.ones(1),
        noise=np.ones(2),
        radius=np.ones(4),
        weights=np.ones(100),
    )
    _test_correct_n_particles(model)


def test_input_too_long():
    model = VicsekModel(
        10,
        1,
        speed=1,
        noise=1,
        radius=1,
        weights=1,
    )
    with pytest.raises(ValueError):
        model.speed = np.ones(101)
    with pytest.raises(ValueError):
        model.noise = np.ones(101)
    with pytest.raises(ValueError):
        model.radius = np.ones(101)
    with pytest.raises(ValueError):
        model.weights = np.ones(101)


def _test_same_state(model1, model2):
    np.testing.assert_array_equal(model1.positions, model2.positions)
    np.testing.assert_array_equal(model1.headings, model2.headings)
    np.testing.assert_array_equal(model1.velocities, model2.velocities)


def test_reproducibility():
    model1 = VicsekModel(
        10,
        1,
        speed=1,
        noise=1,
        seed=12345,
    )
    model2 = VicsekModel(
        10,
        1,
        speed=1,
        noise=1,
        seed=12345,
    )
    _test_same_state(model1, model2)

    model1.evolve(steps=100)
    model2.evolve(steps=100)
    _test_same_state(model1, model2)
