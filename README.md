# Vicsek

An implementation of the 2-dimensional Vicsek model<sup>1</sup> of interacting self-propelled particles, written in Python.

Originally written in Spring 2017 as part of an undergraduate group project.
Rewritten from scratch in Python 3 during Covid-19 lockdown in 2021.

Intended to spark joy.

## Installation

Clone the repo using one of the numerous available options, e.g.
```bash
git clone https://github.com/marshrossney/vicsek.git
cd vicsek
```

The required packages are reasonably up-to-date versions of
* NumPy, SciPy, Matplotlib
* [ConfigArgParse](https://github.com/bw2/ConfigArgParse) if you want to run things via the command line

You can install the Conda environment provided in this repository
```bash
conda create -f environment.yml
conda activate vicsek
```
and then install the package into this environment (make sure you're in the base directory of the repo)
```bash
python -m pip install -e .
```

## Usage

### In Python scripts

For example,
```python
from vicsek.model import VicsekModel
model = VicsekModel(length=100, density=0.1, speed=0.5, noise=2)
# Look at the dynamics
model.animate(steps=100)
# view the final configuration as a quiver plot
model.plot_state()
# print the value of the order parameter
print(model.order_parameter)
# reset to random initial configuration
model.init_state()
# Get the mean and variance of the order parameter based on the final
# configurations of 10 replica models evolved for 200 steps each
mean, var = model.evolve_ensemble(ensemble_size=10, steps=200)
```

### Jupyter notebook

(Requires Jupyter to be installed)

To do. Example notebook in progress.

### Command line

(Requires ConfigArgParse to be installed)

Currently there are three scripts available to run via the command line.
You can provide parameters as command line arguments or collect them together in a config file (recommended).
Look in the `examples` folder for example config files.

#### Animations

```bash
vic-anim -l 100 -d 0.1 --steps 400 --anneal --anneal-periods 0.5
```
will run a simulation in which the noise is annealed over the course of 400 steps, and save the result as as `animation.gif`

#### Visualise evolution of order parameter

This is useful to seeing how many steps are required for simulations to start fluctuating around a fairly stable mean value of the order parameter.

```bash
vic-evol -l 100 -d 0.1 --ensemble-size 10 --steps 100 -i
```
will run an ensemble of 10 models for 100 steps each, and then (thanks to the `-i` flag) prompt the user to continue running, or stop and save the plot.

#### Timings

This essentially just wraps around `timeit.

```bash
vic-time -l 100 -d 0.1 --steps 100 --repeats 10
```

## References
<sup>1</sup> T. Vicsek *et al.*, Phys. Rev. Lett. **75**, 1226 (1995)
