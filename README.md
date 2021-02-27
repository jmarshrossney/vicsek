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
conda create -n vicsek -f environment.yml
conda activate p1b
```
and then install the package into this environment (make sure you're in the base directory of the repo)
```bash
python -m pip install -e .
```

## Usage

### Command line


## References
<sup>1</sup> T. Vicsek *et al.*, Phys. Rev. Lett. **75**, 1226 (1995)
