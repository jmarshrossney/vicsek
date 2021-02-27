import configargparse

parser = configargparse.ArgParser()

parser.add("-c", "--config", is_config_file=True, help="path to config file")

# Arguments specifying model parameters
parser.add("-l", "--length", type=int, required=True, help="side length of box")
parser.add(
    "-d", "--density", type=float, required=True, help="density of agents in box"
)
parser.add(
    "--speed",
    type=float,
    nargs="*",
    default=1,
    help="speed of agents, default: 1",
)
parser.add(
    "--noise",
    type=float,
    nargs="*",
    default=0,
    help="magnitude of noise, default: 0",
)
parser.add(
    "--radius",
    type=float,
    nargs="*",
    default=2,
    help="radius of interaction, default: 2",
)
parser.add(
    "--weights",
    type=float,
    nargs="*",
    default=1,
    help="relative weights of agents in interaction, default: 1",
)

# Arguments specifying simulation parameters
parser.add(
    "--reproducible", action="store_true", help="use known seed for reproducibility"
)
parser.add("--steps", type=int, default=100, help="number of steps to take")
parser.add("-o", "--outpath", type=str, default=".", help="path to output files")
parser.add(
    "--anneal", action="store_true", help="anneal the noise during the simulation"
)
parser.add(
    "--anneal-periods", type=float, default=1.0, help="number of annealing cycles"
)

# Timing measurements
parser.add(
    "--repeats", type=int, default=10, help="number of repeats for timings measurements"
)

# Ensemble evolution
parser.add(
    "--ensemble-size",
    type=int,
    default=10,
    help="number of replica systems to simulate",
)
parser.add(
    "--interval",
    type=int,
    default=10,
    help="steps between order parameter calculations",
)
parser.add(
    "-i",
    "--interactive",
    action="store_true",
    help="run ensemble evolution interactively",
)
