import numpy as np
from scipy.spatial.distance import pdist, squareform
from params import *


def init(L, N, v0, R, eta):
    ''' Initialise a single run '''
    state = np.zeros( (N, 5) )
    state[:,:2] = L*np.random.random( (N, 2) ) - 0.5*L # positions x,y
    state[:,2] = 2*np.pi * np.random.random(N) # angle
    state[:,3] = v0 * np.cos(state[:,2]) # x velocity
    state[:,4] = v0 * np.sin(state[:,2]) # y velocity
    
    return state


def step(state, L, N, v0, R, eta, t): 
    ''' Perform one step for all particles '''
    
    # Update positions
    state[:,:2] = state[:,:2] + v0*dt*state[:,3:]
    
    # Periodic boundaries
    crossedX = np.where(abs(state[:,0]) > 0.5*L)
    crossedY = np.where(abs(state[:,1]) > 0.5*L)
    state[crossedX,0] = state[crossedX,0] - np.sign(state[crossedX,0])*L
    state[crossedY,1] = state[crossedY,1] - np.sign(state[crossedY,1])*L
        
    # Initialise heading with noise
    heading = eta*np.random.random(N) - 0.5*eta
    
    # Use adjacency matrix to determine neighbours
    A = squareform(pdist(state[:,:2]))
    for i in range(N):
        adj = np.where(A[i,:] < R)[0] # indices of adjacent particles
        theta = state[adj,2] # angles of all adjacent particles

        # Leaders must be treated separately on account of their weight
        ldr_adj = np.where(A[i,:N_ldr] < ldr_R)[0]
        ldr_theta = state[ldr_adj,2]

        # Sum sin and cos of angles
        sum_sin = np.sum(np.sin(theta)) + ldr_weight*np.sum(np.sin(ldr_theta))
        sum_cos = np.sum(np.cos(theta)) + ldr_weight*np.sum(np.cos(ldr_theta))
        
        # Compute heading for this particle
        heading[i] += np.arctan2(sum_sin, sum_cos)
   
    # Update state with new headings
    state[:,2] = heading # Can add an angle here for waveyness
    
    # Some leaders may have pre-defined trajectories
    state[:N_ldr_traj,2] = ldr_traj * t
     
    # Update velocities
    state[:,3] = v0 * np.cos(state[:,2])
    state[:,4] = v0 * np.sin(state[:,2])
    
    return
        

def order_parameter(state, V_coeff):
    ''' Calculate order parameter (V) '''
    
    Vx = np.sum(state[:,3])
    Vy = np.sum(state[:,4])
    return np.sqrt(Vx*Vx + Vy*Vy) * V_coeff
    
