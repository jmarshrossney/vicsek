import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as mpl_pdf
import matplotlib.gridspec as gridspec
from sys import argv, exit

from params import *

# Third argument variable can tell us to save figure(s)
if len(argv) > 3 and argv[3] == 'save':
    save = True
else:
    save = False

#####################
## Plot a snapshot ##
#####################
if argv[1] == 'state':

    # Load data given as second argument variable
    input_data = np.loadtxt(argv[2])
    
    # Separate into parameters and state
    L, N, v0, R, eta = input_data[0,:]
    state = input_data[1:,:]

    # Create plot without axes or ticks
    fig, ax = plt.subplots()
    ax.set_title("$L=$%g, $N=$%g, $v_0=$%g, $R=$%g, $\eta=$%g" %(L,N,v0,R,eta))
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

    # Plot positions and velocities
    ax.quiver(state[:,0], state[:,1], state[:,3], state[:,4])

    # If argv[3] = save, save the figure
    if save == True:
        fig_file = argv[2].replace('.out','.png')
        fig.savefig(fig_file)

    plt.show()
   

    exit(0)


#####################
## Plot statistics ##
#####################
# Argument variables tell us how to organise the data into plots
# Possible values:   'N', 'v0', 'R', 'eta'
x_var = argv[1] # values of this variable on the x-axis
lines_var = argv[2] # values of this variable are different lines on the same plot

# Open pdf for saving
if save == True:
    save_pdf = mpl_pdf.PdfPages(save_name+".pdf")

# Quick check that argument variables are valid
plot_vars = ['N','v0','R','eta']
if x_var not in plot_vars or lines_var not in plot_vars:
    print "Error: invalid argument(s)"
    exit(1)

# The other two variables will be separated into separate plots
plot_vars.remove(x_var)
plot_vars.remove(lines_var)

# Load data output by main.py
save_file = save_name + ".out"
input_data = np.loadtxt(save_file)

# Create dictionary to link string variables with indices for input_data
index_dict = {'L': 0, 'N': 1, 'v0': 2, 'R': 3, 'eta': 4,
              'V': 5, 'eV': 6, 'chi': 7, 'echi': 8, 'U': 9, 'eU': 10}

# Dictionary so that the x-label and plot symbols are a little more fancy
xlabel_dict = {'N': "Number of particles", 'v0': "Particle velocity",
               'R': "Interaction radius", 'eta': "Magnitude of heading noise"}
symb_dict = {'N': "$N$", 'v0': "$v_0$", 'R': "$R$", 'eta': "$\eta$"}


# Iterate over unique values of the first variable in plot_vars
for I in set(list( input_data[:, index_dict[plot_vars[0]] ] )):
    Irows = np.where( input_data[:, index_dict[plot_vars[0]] ] == I )[0]
    Idata = input_data[Irows, :]
    
    # Now over unique values of the second variable in plot_vars
    for J in set(list( Idata[:, index_dict[plot_vars[1]] ] )):
        IJrows = np.where( Idata[:, index_dict[plot_vars[1]] ] == J )[0]
        IJdata = Idata[IJrows, :]

        # Create plots
        fig = plt.figure(figsize=(8,4))
        gs = gridspec.GridSpec(1, 3, width_ratios=[1,1,1])
        ax = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1])
        ax3 = plt.subplot(gs[2])
        
        ax2.set_title("%s = %g, %s = %g" 
                %(symb_dict[plot_vars[0]], I, symb_dict[plot_vars[1]], J) )
        ax.set_ylabel("Order parameter ($V$)")
        ax2.set_ylabel("Susceptibility ($\chi$)")
        ax3.set_ylabel("Binder cumulant ($U$)")
        ax.set_xlabel(xlabel_dict[x_var]+" ("+symb_dict[x_var]+")")
        ax2.set_xlabel(xlabel_dict[x_var]+" ("+symb_dict[x_var]+")")
        ax3.set_xlabel(xlabel_dict[x_var]+" ("+symb_dict[x_var]+")")

        # For each unique value of lines_var, plot a line
        for K in set(list( IJdata[:, index_dict[lines_var] ] )):
            IJKrows = np.where( IJdata[:, index_dict[lines_var] ] == K )[0]
            IJKdata = IJdata[IJKrows, :]

            # x_var plotted along x-axis
            xdata = IJKdata[:, index_dict[x_var] ]

            # Get indices which sort xdata into ascending order
            srted = np.argsort(xdata)
            xdata = xdata[ srted ]
            
            # Plot Order parameter, susceptibility and Binder cumulent
            ax.errorbar(xdata, IJKdata[srted, index_dict['V'] ], 
                    yerr=IJKdata[srted, index_dict['eV'] ], fmt='.-')
            ax2.errorbar(xdata, IJKdata[srted, index_dict['chi'] ], 
                    yerr=IJKdata[srted, index_dict['echi'] ], fmt='.-')
            ax3.errorbar(xdata, IJKdata[srted, index_dict['U'] ], 
                    yerr=IJKdata[srted, index_dict['eU'] ], fmt='.-',
                    label="%s=%g" %(symb_dict[lines_var],K) )

        ax3.legend()
        plt.tight_layout()
    
        # Add the figure to the open pdf file
        if save == True:
            save_pdf.savefig(fig)
        
        plt.show()

# Close the pdf
if save == True:
    save_pdf.close()

