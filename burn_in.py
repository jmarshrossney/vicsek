import numpy as np
import matplotlib.pyplot as plt
from sys import argv

from params import *
import model

###############################################################
## Measure burn-in time for different parameter combinations ##
###############################################################

# Set noise to 0 for all simulations
eta = 0

# v0, R are the first values of v0_list and R_list
v0 = v0_list[0]
R = R_list[0]

# Print parameters
print "Computing burn-in times for the following parameters:"
print "(v0, R, eta) = (%g, %g, 0)" %(v0,R)
print "dt = %g" %dt

# Want to track how far we are through the parameter combinations
numN = len(N_list)
iN = 0

# Initialise lists to hold all results
nt_burn_mean = np.zeros(numN)
nt_burn_stderr = np.zeros(numN)

# Loop over particle numbers
for N in N_list:
    
    # Adjust L if fixed density
    if fixed_density == True:
        L = np.sqrt(N/density)
    else:
        L = L0
    
    V_coeff = 1.0 / (N*v0)
    
    # Create empty arrays for repeats
    nt_burn_repeats = np.zeros(repeats)
    
    print ""
    print "(L, N) = (%g, %g)" %(L,N)

    # Loop over repeats
    print "Simulation:"
    for rep in range(repeats):

        # Print current repeat number
        print "            %d/%d" %(rep+1,repeats)

        # Create a brand new initial state
        state = model.init(L, N, v0, R, eta)
               
        # Initialise V, t and set V_coeff
        V = 0
        t = 0

        # Loop over steps until order parameter hits threshold
        while V < 0.98:
                    
            # All particles take one step
            model.step(state, L, N, v0, R, eta, t)
            V = model.order_parameter(state, V_coeff)
            t += 1

        # Save steps to burn in
        nt_burn_repeats[rep] = t

    # End loop over repeats

    # Compute mean and standard deviation of burn-in time
    nt_burn_mean[iN] = np.mean(nt_burn_repeats)
    nt_burn_stderr[iN] = np.std(nt_burn_repeats) / np.sqrt(repeats)
    
    iN += 1


# End loop over particle numbers


##########################
## Plot and attempt fit ##
##########################

fig, ax = plt.subplots()
ax.set_title("Burn-in time for (v0, R, eta) = (%g, %g, 0)" %(v0,R))
ax.set_xlabel("Number of particles")
ax.set_ylabel("Number of steps to reach V = 0.98")

# Plot measured times
ax.errorbar(N_list, nt_burn_mean, yerr=nt_burn_stderr, fmt='ko')

# Linear fit with weights = 1 / error
coeffs = np.polyfit(N_list, nt_burn_mean, 1, w=1.0/nt_burn_stderr)
print "Fit: nt_burn = %g x N + %g" %(coeffs[0],coeffs[1])

# Plot fit
fit = np.array(N_list)*coeffs[0] + coeffs[1]
ax.plot(N_list, fit, 'r--')

plt.show()

