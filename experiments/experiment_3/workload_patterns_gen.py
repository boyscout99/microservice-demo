"""
This script is used to generate workload patterns
by providing the RPS for each timestep.
"""
import numpy as np
import matplotlib.pyplot as plt

# to plot it, create an array of TIMESTAMPS length, an array of rps values

class WorkloadGenerator:
    """
    You can generate different types of signals.
    """
    # function for steps
    def step_function(timesteps, minRPS, maxRPS, steps):
        """
        Create an increasing step function, with even spaced intervals.
        """
        x_timesteps = list(range(0,timesteps))
        y_rps = []
        # divide timesteps in steps 
        for i in range(0,timesteps):
            # RPS per interval
            rps_per_interval = (maxRPS-minRPS)/steps
            value = minRPS + rps_per_interval*(np.floor(i/(timesteps/steps)))
            y_rps.append(value)
        
        # plt.plot(x_timesteps, y_rps)
        # plt.show()
        
        return x_timesteps, y_rps
    
    # function for steps
    def decr_step_function(timesteps, minRPS, maxRPS, steps):
        """
        Create an increasing step function, with even spaced intervals.
        """
        x_timesteps = list(range(0,timesteps))
        y_rps = []
        # divide timesteps in steps 
        for i in range(0,timesteps):
            # RPS per interval
            rps_per_interval = (maxRPS-minRPS)/steps
            value = maxRPS - rps_per_interval*(np.floor(i/(timesteps/steps)))
            y_rps.append(value)
        
        # plt.plot(x_timesteps, y_rps)
        # plt.show()
        
        return x_timesteps, y_rps


    # function for sin(x)
    def sin_function(timesteps, minRPS, maxRPS, periods):
        """
        Create a sinusoidal function of length timesteps
        """
        x_timesteps = np.arange(0, 2*np.pi, 2*np.pi/timesteps) # in radians
        # constrain y_rps between minRPS and maxRPS
        y_rps = (maxRPS + minRPS)/2 + (maxRPS-(maxRPS + minRPS)/2)*np.sin(x_timesteps*periods)

        # plt.plot(x_timesteps, y_rps)
        # plt.show()

        return x_timesteps, y_rps

    # function for random(x)
    def sin_spikes_function(timesteps, minRPS, maxRPS, periods, spike_probability):
        """
        Add random spikes to a sinusoidal function.
        """
        # Parameters
        spike_height_range = (-(maxRPS - minRPS)/4, (maxRPS - minRPS)/4)  # Range of spike heights
        spike_duration_range = (5, 20)  # Range of spike durations in timesteps

        x_timesteps = np.arange(0, 2*np.pi, 2*np.pi/timesteps) # in radians
        # constrain y_rps between minRPS and maxRPS
        y_rps = (maxRPS + minRPS)/2 + (maxRPS/2-(maxRPS + minRPS)/4)*np.sin(x_timesteps*periods)

        # Add spikes at random intervals
        for i in range(timesteps):
            if np.random.rand() < spike_probability:
                spike_height = np.random.uniform(*spike_height_range) # unpack tuple
                spike_duration = np.random.randint(*spike_duration_range) # unpack tuple
                y_rps[i:i+spike_duration] += spike_height
                i += spike_duration

        # Plot the function
        # plt.plot(x_timesteps, y_rps)
        # plt.show()

        return x_timesteps, y_rps

# if __name__ == '__main__':
    # y_rps = step_function(81, 52.5, 1250, 15)
    # y_rps = sin_function(300, 50, 750, 2)
    # print(f"y_rps: {y_rps}")
    # y = sin_spikes_function(300, 50, 100, 3, 0.05)