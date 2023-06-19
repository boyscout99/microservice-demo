"""
This script is used to generate workload patterns
by providing the RPS for each timestep.
"""
import numpy as np
import matplotlib.pyplot as plt

# to plot it, create an array of TIMESTAMPS length, an array of rps values


# function for steps
def step_function(timesteps, minRPS, maxRPS, steps):
    """
    Create an increasing step function, with even spaced intervals.
    """
    x_timesteps = list(range(1,timesteps))
    y_rps = []
    # divide timesteps in steps 
    for i in range(1,timesteps):
        # RPS per interval
        rps_per_interval = (maxRPS-minRPS)/steps
        value = minRPS + rps_per_interval*(np.floor(i/(timesteps/steps)))
        y_rps.append(value)
    
    plt.plot(x_timesteps, y_rps)
    plt.show()
    
    return y_rps


# function for sin(x)

# function for random(x)

if __name__ == '__main__':
    y_rps = step_function(81, 52.5, 1250, 15)
    print(f"y_rps: {y_rps}")