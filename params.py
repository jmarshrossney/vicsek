import numpy as np


# ----------------------- #
#  Simulation parameters  #
# ----------------------- #
tf = 5000. # final time
dt = 1. # timestep
nt = int(tf/dt) # No. timesteps

''' fixed_density != True  results in a box with sides [-L0/2, L0/2].
    fixed_density = True  rescales the box size according to L = sqrt(N/density) '''
fixed_density = False
L0 = 10.
density = 0.5

''' The following parameters must given as lists/tuples/arrays.
    So a single value must be given as e.g. [x,] or (x,)
    When running from main.py, all combinations will be iterated over.
    When running an animation, the first/only values will be used. '''
N_list = (300,)#, 150, 200, 250, 300,)            # number of particles
v0_list = (0.15,)                    # velocity as a fraction of L
R_list = (1.0,)                     # interaction radius as a fraction of L
eta_list = (0.1,)#list(np.linspace(0.01,0.5,10))+list(np.linspace(0.5,5.0,20))  # noise


# ----------------- #
#  Parallelisation  #
# ----------------- #
Np = 1 # Number of processes


# -------------------- #
#  Data and averaging  #
# -------------------- #
''' Ideally, the time for which the simulation is left to 'burn in' (before data
    is taken) should scale appropriately with different parameter combinations.
    Run python burn_in.py for the SMALLEST values of v0 & R you're using (these are
    the slowest to burn in). This will fit a straight line for the burn-in time
    dependence on N, with coefficients which you should assign to burn_coeff below.
    You might want to run simulations with very different v0, R separately so that
    they don't all need to have the slowest burn-in time.
    WARNING: this doesn't work too well for large systems, small but non-zero eta!'''
burn_coeff = [0, 1] # nt_burn = burn_coeff[0] x N + burn_coeff[1]

# Number of repeated simulations per set of parameters. Minimum 2!
repeats = 2

# Number of samples involved in susceptibility and Binder cumulant error determination
error_samples = 50

# Save file name for statistics (do not include extension: .out will be added automatically)
save_name = "output"

# Save a snapshot of the final state for each parameter combination
save_snapshots = True

# --------- #
#  Leaders  #
# --------- #
N_ldr = 0 # number of leaders
ldr_weight = 9 # effective weight - no. normal particles in leader
ldr_R = 1.5 # multiple of regular interaction radius

''' Can have multiple leaders with different trajectories. These are angular frequencies,
    so they will be multiplied by the current time. The N_ldr-N_ldr_traj leaders without
    a pre-defined trajectory will obey the same rules as normal particles. '''
ldr_traj = np.array([0.02]) # numpy array
N_ldr_traj = min(len(ldr_traj), N_ldr)


# ----------- #
#  Animation  #
# ----------- #
ms = 3 # blob size
lms = np.sqrt(ldr_weight)*ms # leader blob size

''' Set do_plots to True to include animated plots of the order parameter (V) and
    susceptibility (chi). This makes the animation a little slower. '''
do_plots = False # can be overridden using argv[1]=plot: python animate.py plot
window = 50 # number of steps to average over for V,chi plots
plot_step = 10 # number of steps to take before computing and adding new data to OP+sus plots

# Run through values of eta between eta_start & eta_finish
eta_start = 7.
eta_finish = 0.
N_eta_vals = 35
steps_per_eta_val = 50 # int



