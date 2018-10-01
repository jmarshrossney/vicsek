import numpy as np
from sys import argv

from params import *
import model

# For parallel runs, index for this process given as argv
if len(argv) > 1:
    pid = int(argv[1])

    # Separate save files for different processes
    save_file = save_name + "_p" + str(pid) + ".out"

else:
    pid = 0
    save_file = save_name + ".out"


# eta_list is partitioned between the processes
eta_list = eta_list[pid::Np]

print ""
print "------------------"
print "| Process no. %02d |" %pid
print "------------------"
print ""
print "General simulation info:"
if fixed_density == True:
    print "     Fixed density: %g" %density
else:
    print "     Box size: %g x %g" %(L0,L0)
print "     Simulation time: %g in %g steps of size %g" %(tf,nt,dt)
print "     %d leaders active" %N_ldr
print "     Save file: %s" %save_file


# Want to track how far we are through the parameter combinations
parameter_combinations = len(N_list) * len(v0_list) * len(R_list) * len(eta_list)
icomb = 0

# Loop over particle numbers
for N in N_list:
    
    # Adjust L if fixed density
    if fixed_density == True:
        L = np.sqrt(N/density)
    else:
        L = L0
    
    # Number of steps for burn-in period
    nt_burn = int( round(burn_coeff[0]*N + burn_coeff[1]) )
        
    # Loop over velocities
    for v0 in v0_list:
        # Loop over interaction radii
        for R in R_list:
            # Loop over noise values
            for eta in eta_list:

                # Print current parameters
                icomb += 1
                print ""
                print "Parameter combination %d/%d" %(icomb, parameter_combinations)
                print "Current parameters: (N, v0, R, eta) = (%d, %g, %g, %g)" %(N,v0,R,eta)
                print "%d steps for burn-in, %d steps with data-taking" %(nt_burn,nt)

                # Create empty arrays for repeats
                V_mean_repeats = np.zeros(repeats)
                Vsq_mean_repeats = np.zeros(repeats)
                Vqu_mean_repeats = np.zeros(repeats)

                # Loop over repeats
                print "Simulation:"
                for rep in range(repeats):

                    # Print current repeat number
                    print "            %d/%d" %(rep+1,repeats)

                    # Create a brand new initial state
                    state = model.init(L, N, v0, R, eta)

                    # Burn-in period
                    for t in range(nt_burn):

                        # All particles take one step
                        model.step(state, L, N, v0, R, eta, t)

                    # Create empty array for order parameter time-series
                    V_series = np.zeros(nt)
       
                    # Coefficients
                    V_coeff = 1.0 / (N*v0) # normalisation factor for order parameter
                    chi_coeff = L**2 # N/density
                    
                    # Loop over steps
                    for t in range(nt):
                        
                        # All particles take one step
                        model.step(state, L, N, v0, R, eta, t)
                        
                        # Order parameter is tracked
                        V_series[t] = model.order_parameter(state, V_coeff)
 
                    # Powers of the order parameter (that sounds cool)
                    Vsq_series = V_series * V_series
                    Vqu_series = Vsq_series * Vsq_series

                    # Mean of these time series' added to arrays of repeats
                    V_mean_repeats[rep] = np.mean(V_series)
                    Vsq_mean_repeats[rep] = np.mean(Vsq_series)
                    Vqu_mean_repeats[rep] = np.mean(Vqu_series)

                # End loop over repeats

                # Compute mean of multiple independent simulations
                V_mean = np.mean(V_mean_repeats)
                eV_mean = np.std(V_mean_repeats, ddof=1) / np.sqrt(repeats) # Std err on mean
                Vsq_mean = np.mean(Vsq_mean_repeats)
                Vqu_mean = np.mean(Vqu_mean_repeats)
               
                # Compute sample variance
                ''' This gives +ve definite results with a much smaller error than obtained
                    via method used below for Binder cumulant, which would involve 
                    sampling V, V^2 and using var = <V^2> - <V>^2.'''
                V_var = np.var(V_mean_repeats, ddof=1)
                eV_var = V_var * np.sqrt(2.0/(repeats-1)) # Std err on variance
                
                # Get susceptibility from variance
                chi = V_var * chi_coeff
                echi = eV_var * chi_coeff

                # Compute Binder cumulant
                ''' Use the Central Limit Theorem to obtain a normal distribution for
                    the Binder cumulant, through sampling V^2 and V^4 distributions.
                    This performs better than using only the mean of V^2 and V^4 and 
                    propagating standard errors on these means. '''
                Vsq_std = np.std(Vsq_mean_repeats, ddof=1)
                Vqu_std = np.std(Vqu_mean_repeats, ddof=1)
                U_dist = np.zeros(error_samples)
                for sample in range(error_samples):

                    # Reject samples below 0 or above 1
                    Vsq_sample = -1
                    Vqu_sample = -1
                    while Vsq_sample < 0 or Vsq_sample > 1:
                        Vsq_sample = np.random.normal(Vsq_mean, Vsq_std)
                    while Vqu_sample < 0 or Vqu_sample > 1:
                        Vqu_sample = np.random.normal(Vqu_mean, Vqu_std)
                    
                    # Compute Binder cumulant for these samples
                    U_dist[sample] = 1 - ( Vqu_sample / (3*Vsq_sample**2) )
                
                # Compute mean and standard error of Binder cumulant
                U = np.mean(U_dist)
                eU = np.std(U_dist) / np.sqrt(error_samples)

                # Save results
                print "Saving results to ", save_file
                with open(save_file, 'a') as f:
                    f.write( "%f %d %f %f %f %f %f %f %f %f %f \n" \
                            %(L, N, v0, R, eta, V_mean, eV_mean, chi, echi, U, eU) )
                
                # Save snapshot of final state for final repeat
                if save_snapshots == True:

                    # Create string for file name
                    snap_name = "snapshot_L%g_N%g_v%g_R%g_eta%g_t%d" %(L,N,v0,R,eta,int(nt*dt))
                    snap_file = snap_name.replace('.','-') + ".out"

                    # First line will be the parameters
                    snapshot = np.zeros( (N+1, 5) )
                    snapshot[0,:] = [L, N, v0, R, eta]
                    snapshot[1:,:] = state

                    print "Saving snapshot of final state to ", snap_file
                    np.savetxt(snap_file, snapshot)

                            
            # End loop over noise values
        # End loop over interaction radii
    # End loop over velocities
# End loop over particle numbers


