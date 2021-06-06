# Vicsek

An implementation of the 2-dimensional Vicsek model<sup>1</sup> of interacting self-propelled particles, written in Python.

Originally written in Python 2 as part of an undergraduate group project. Recently updated to Python 3 and completely reformulated because people had actually been forking some embaressingly shit code for their projects and I felt very guilty.

Intended to spark joy :)

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

To do

## To do

Things I will definitely do:
- [ ] Add example config files and outputs, e.g. to replicate original results of Ref.<sup>1</sup>
- [ ] Add a couple of Jupyter notebooks to demonstrate usage
- [ ] Add tests

Things I would like to do:
- [ ] Improve the speed
- [ ] Allow for saving and loading from checkpoint files
- [ ] Implement some more active matter models - Active Brownian Particles, Metric-free Vicsek etc.
- [ ] Upgrade configargparse to jsonargparse because it looks really nice

## References
<sup>1</sup> T. Vicsek *et al.*, Phys. Rev. Lett. **75**, 1226 (1995)
