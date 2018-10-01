import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.gridspec as gridspec
from sys import argv, exit

from params import *
import model

# Override params if argv[1] == plot
if len(argv) > 1:
    if argv[1] == 'plot': do_plots = True

# Take the first values in the lists of parameters given in params.py
N = N_list[0]
v0 = v0_list[0]
R = R_list[0]

# If fixed density, adjust box size
if fixed_density == True:
    L = np.sqrt(N/density)
else:
    L = L0

# Eta steps through the values in this array
eta_vals = np.linspace(eta_start, eta_finish, N_eta_vals)
eta_i = 0
eta_i_max = N_eta_vals - 1


# Coefficicents
V_coeff = 1.0 / (N*v0) # normalisation factor for order parameter
chi_coeff = L**2 # N/density


############################
## Animate particles only ##
############################
def animate():
    
    # Initialise model
    state = model.init(L, N, v0, R, eta_start)

    # Create plot without axes or ticks
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(bottom='off', left='off')
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_aspect('equal')
    
    # Create box
    box = plt.Rectangle((-L/2,-L/2), L, L, ec='none', lw=3, fc='none')
    box.set_edgecolor('k')
    ax.add_patch(box)

    # Text displaying current value of noise
    eta_text = ax.text(0.65*(L/2), 1.03*(L/2), "", fontsize=8)
   
    # Initialise particles and leaders
    particles, = ax.plot([], [], 'bo')
    leaders, = ax.plot([], [], 'mo')
    particles.set_markersize(ms)
    leaders.set_markersize(lms)

    def init():
        particles.set_data([], [])
        leaders.set_data([], [])
        eta_text.set_text("%.3f" %eta_start)
        return particles, leaders, box, eta_text
                
    def update(t):
               
        # Get eta for this timestep (integer divide isn't too slow)
        eta_i = min(t/steps_per_eta_val, eta_i_max)
        eta = eta_vals[eta_i]
        eta_text.set_text("$\eta=$%g" %eta)

        # All particles take one step
        model.step(state, L, N, v0, R, eta, t)
        t = t+1
    
        # Update animation
        particles.set_data(state[:, 0], state[:, 1])
        leaders.set_data(state[range(N_ldr),0], state[range(N_ldr),1])
        
        return particles, leaders, box, eta_text

    ani = anim.FuncAnimation(fig, update, interval=10, blit=True, init_func=init)

    plt.tight_layout()
    plt.show()
    
    return ani
    

###########################################################
## Animate particles, order parameter and susceptibility ##
###########################################################
def animate_plots():
    
    # Initialise model
    state = model.init(L, N, v0, R, eta_start)

    # Create plots with size ratio
    fig = plt.figure(figsize=(12,6))
    gs = gridspec.GridSpec(1, 3, width_ratios=[2,1,1])
    ax = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])
    ax3 = plt.subplot(gs[2])
   
    # Particles animation
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(bottom='off', left='off')
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_aspect('equal')

    # Create box
    box = plt.Rectangle((-L/2,-L/2), L, L, ec='none', lw=3, fc='none')
    box.set_edgecolor('k')
    ax.add_patch(box)
    
    # Text displaying current value of noise
    eta_text = ax.text(0.65*(L/2), 1.03*(L/2), "", fontsize=8)
   
    # Initialise particles and leaders
    particles, = ax.plot([], [], 'bo')
    leaders, = ax.plot([], [], 'mo')
    particles.set_markersize(ms)
    leaders.set_markersize(lms)

    # Order parameter
    ax2.set_title("Order parameter")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("V")
    ax2.set_ylim(0, 1.0)
    V_plot, = ax2.plot([], [], 'g')
    V_series = []
    V_mean_series = []
    t_series = []

    # Susceptibility
    ax3.set_title("Susceptibility")
    ax3.set_xlabel("Time")
    ax3.set_ylabel("$\chi$")
    chi_plot, = ax3.plot([], [], 'r')
    chi_series = []

    def init():
        particles.set_data([], [])
        leaders.set_data([], [])
        eta_text.set_text("%.3f" %eta_start)
        V_plot.set_data([], [])
        chi_plot.set_data([], [])
        return particles, leaders, box, eta_text, V_plot, chi_plot
                
    def update(t):
        
        # Get eta for this timestep
        eta_i = min(t/steps_per_eta_val, eta_i_max)
        eta = eta_vals[eta_i]
        eta_text.set_text("$\eta=$%g" %eta)
        
        # All particles take one step
        model.step(state, L, N, v0, R, eta, t)
        V = model.order_parameter(state, V_coeff)
        V_series.append(V)
        t = t+1
        
        # Update particle animation
        particles.set_data(state[:, 0], state[:, 1])
        leaders.set_data(state[range(N_ldr),0], state[range(N_ldr),1])
       
        # Take average of 'window' data points every 'plot_step' steps
        if t > window and t % plot_step == 0:
            # Do averages
            V_window = np.array(V_series[-window:])
            V_mean = np.mean(V_window)
            Vsq_mean = np.mean(V_window*V_window)
            chi = chi_coeff * (Vsq_mean - V_mean*V_mean)
            
            # Update data lists
            V_mean_series.append(V_mean)
            chi_series.append(chi)
            t_series.append(t*dt)
            
            # Update animated plots
            V_plot.set_data(t_series, V_mean_series)
            chi_plot.set_data(t_series, chi_series)

            # Update limits if necessary
            tmax = ax2.get_xlim()[1]
            chimax = np.max(chi_series)
            if t > tmax or chi > chimax:
                ax2.set_xlim(0, 2*tmax)
                ax3.set_xlim(0, 2*tmax)
                ax3.set_ylim(0, 1.1*chimax)
                ax2.figure.canvas.draw()
                ax3.figure.canvas.draw()
            
        return particles, leaders, box, eta_text, V_plot, chi_plot
    
    ani = anim.FuncAnimation(fig, update, interval=10, blit=True, init_func=init)

    plt.tight_layout()
    plt.show()
    
    return ani
    

if do_plots == True:
    outer_ani = animate_plots()
else:
    outer_ani = animate()

