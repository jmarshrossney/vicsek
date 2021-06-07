import configargparse

parser = configargparse.ArgParser()

parser.add("-c", "--config", is_config_file=True, help="path to config file")
parser.add("-o", "--outpath", type=str, default=".", help="path to output files")

# Arguments specifying model parameters
parser.add("-l", "--length", type=int, required=True, help="side length of box")
parser.add(
    "-d", "--density", type=float, required=True, help="density of particles in box"
)
parser.add(
    "--speed",
    type=float,
    required=True,
    nargs="*",
    help="speed of particles",
)
parser.add(
    "--noise",
    type=float,
    required=True,
    nargs="*",
    help="magnitude of noise",
)
parser.add(
    "--radius",
    type=float,
    nargs="*",
    default=1,
    help="radius of interaction, default: 1",
)
parser.add(
    "--weights",
    type=float,
    nargs="*",
    default=1,
    help="relative weights of particles in interaction, default: 1",
)
parser.add("--seed", type=int, default=None, help="provide integer seed for reproducibility")

parser.add(
    "--style", type=str, default=None, help="path to custom matplotlib style file"
)
