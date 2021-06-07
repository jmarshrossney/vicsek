# Vicsek

An implementation of the two-dimensional Vicsek model<sup>1</sup> of interacting self-propelled particles.

Originally written in Python 2 as part of an undergraduate group project back in 2017. Recently updated to Python 3 and completely reformulated because people had actually been forking some embarrassingly shit code for their projects and I felt very guilty.

Intended to spark joy :)

## Installation

### Basic installation

Clone the repo using one of the numerous available options, e.g.

```
git clone https://github.com/marshrossney/vicsek.git
cd vicsek
```

Next, install the Conda environment provided in this repository

```
conda create -f environment.yml -n vicsek
conda activate vicsek
```

and then install the package into this environment

```
python -m pip install -e .
```

This is technically all you need to be able to import modules into your scripts.

To run the scripts in `vicsek/scripts/` from the command line, you will also need to install [ConfigArgParse](https://github.com/bw2/ConfigArgParse).

```
conda install -c conda-forge configargparse
```

### Development

If you want to extend or modify the code I would suggest creating a 'development' environment,

```
conda create -n vicsek-dev --clone vicsek
conda activate vicsek-dev
```

and installing whatever packages you would like to use for development, e.g.

```
conda install -c anaconda ipython
conda install -c conda-forge jupyterlab black
```

### Testing

If you're making changes it's a good idea run tests to make sure the changes didn't introduce unexpected behaviour. 

```
conda install -c anaconda pytest flake8
```

When executed in the base directory of the repository, the following lines will lint the code and run any existing unit tests.
```
flake8 .
pytest
```

### Installation without Conda

The requirements are basically just
* Python 3.9
* Reasonably up-to-date versions of NumPy, SciPy and Matplotlib
* tqdm

It should be fine to just install these via e.g. `pip install`, but I haven't tested it.

## Usage

### In scripts

The most basic usage is

```python
import matplotlib.pyplot as plt

from vicsek.model import VicsekModel
from vicsek.visualize import ParticlesAnimation

model = VicsekModel(
    length=10,
    density=0.5,
    speed=0.3,
    radius=0.6,
)

# View a snapshot of the particles
snapshot = model.view()
plt.show()

# Run an animation
animator = ParticlesAnimation(model)
animation = animator.animate()
plt.show()
```

### Making an animation

TODO

### Evolution of the order parameter

TODO

## To do

Things I will definitely do:
- [ ] Add example config files and outputs, e.g. to replicate original results of Ref.<sup>1</sup>
- [ ] Add a couple of Jupyter notebooks to demonstrate usage
- [ ] Add more tests

Things I would like to do:
- [ ] Improve the speed
- [ ] Allow for saving and loading from checkpoint files
- [ ] Implement some more active matter models - Active Brownian Particles, Metric-free Vicsek etc.
- [ ] Upgrade configargparse to jsonargparse because it looks really nice

## References
<sup>1</sup> T. Vicsek *et al.*, Phys. Rev. Lett. **75**, 1226 (1995)
