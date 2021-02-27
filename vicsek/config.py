import configargparse

parser = configargparse.ArgParser()

parser.add("-f", "--config", is_config_file=True, help="path to config file")

parser.add("-l", "--length", type=int, required=True, help="side length of box")
parser.add(
    "-d", "--density", type=float, required=True, help="density of agents in box"
)
parser.add(
    "--speed",
    type=float,
    action="append",
    default=1,
    help="speed of agents, default: 1.0",
)
parser.add(
    "--radius",
    type=float,
    action="append",
    default=3,
    help="radius of interaction, default: 1.0",
)
parser.add(
    "--noise",
    type=float,
    action="append",
    default=0.0,
    help="magnitude of noise, default: 0.1",
)
parser.add("--weights", type=float, action="append", default=1, help="weights")

parser.add(
    "--reproducible", action="store_true", help="use known seed for reproducibility"
)

parser.add("-o", "--outpath", type=str, default=".", help="path to output files")

parser.add("--steps", type=int, default=100, help="number of steps to take")
parser.add(
    "--repeats", type=int, default=10, help="number of repeats for timings measurements"
)

parser.add(
    "--anneal", action="store_true", help="anneal the noise during the simulation"
)
parser.add(
    "--anneal-periods", type=float, default=1.0, help="number of annealing cycles"
)
parser.add(
    "--anneal-interval", type=int, default=10, help="steps between annealing updates"
)

parser.add(
    "--cmap", type=str, default="viridis_r", help="matplotlib colourmap for animations"
)

parser.add(
    "-i",
    "--interactive",
    action="store_true",
    help="run ensemble evolution interactively",
)

parser.add(
    "--op-interval",
    type=int,
    default=10,
    help="steps between order parameter calculations",
)
parser.add(
    "--ensemble-size",
    type=int,
    default=10,
    help="number of replica systems to simulate",
)
