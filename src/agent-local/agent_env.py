import gym
from gym import spaces
from scale import KubernetesEnvironment
from query import PrometheusClient

import numpy as np

class GymEnvironment(gym.Env):
    def __init__(self, alpha):
        self.alpha = alpha
        self.action_space = spaces.Discrete(3)  # Action space with 3 discrete actions: 1, 0, -1
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.float64)  # Observation space with 4 continuous elements: response time, CPU usage, memory usage, replicas

    def reset(self):
        # Reset the environment, e.g., initialize the pod states and retrieve initial observation
        self.previous_response_time = 0  # Initialize previous response time as 0
        self.current_replicas = 0  # Initialize current number of replicas as 0
        self.current_observation = self._get_observation()  # Retrieve initial observation from Prometheus API
        return self.current_observation

    def step(self, action):
        # Take a step in the environment based on the given action
        # Update the pod states, calculate reward, and return the new observation, reward, done, and info

        # Update the pod states based on the action
        if action == 0:  # No change in replicas
            pass
        elif action == 1:  # Increase replicas
            self.current_replicas += 1
        elif action == 2:  # Decrease replicas
            self.current_replicas -= 1

        # Get the new observation from Prometheus API
        new_observation = self._get_observation()

        # Calculate reward based on the new observation and previous response time
        reward = -(self.alpha * int(new_observation[0] > self.previous_response_time) + self.current_replicas)

        # Update the previous response time for the next step
        self.previous_response_time = new_observation[0]

        # Set done to False as the environment is not terminated in this example
        done = False

        # Set info to an empty dictionary
        info = {}

        return new_observation, reward, done, info

    def _get_observation(self):
        # Retrieve observation from Prometheus API, e.g., query response time, CPU usage, memory usage, and replicas
        

        observation = [0, 0, 0, 0]  # Placeholder observation
        return observation