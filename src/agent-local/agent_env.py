import gym
from gym import spaces

from Scale import KubernetesEnvironment
from Query import PrometheusClient

import numpy as np
import time

class GymEnvironment(gym.Env):
    def __init__(self, alpha, queries, url, name, namespace, minReplicas, maxReplicas):
        self.alpha = alpha

        self.queries = queries
        self.url = url
        self.prom = PrometheusClient(self.url)

        self.name = name
        self.namespace = namespace
        self.minReplicas = minReplicas
        self.maxReplicas = maxReplicas
        self.scale = KubernetesEnvironment(self.name, self.namespace, self.minReplicas, self.maxReplicas)

        self.action_space = spaces.Discrete(3)  # Action space with 3 discrete actions: 1, 0, -1
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.float64)  # Observation space with 4 continuous elements: response time, CPU usage, memory usage, replicas

    def reset(self):
        # Reset the environment, e.g., initialize the pod states and retrieve initial observation
        # TODO do I need to reset the workload pattern?
        self.scale.reset_replicas() # Initialize current number of replicas as 1
        time.sleep(15)

        self.current_observation = self._get_observation()  # Retrieve initial observation from Prometheus API
        self.current_replicas = self.current_observation[0]
        self.previous_response_time = self.current_observation[1]  # Initialize previous response time
        return self.current_observation

    def step(self, action):
        # Take a step in the environment based on the given action
        # Update the pod states, calculate reward, and return the new observation, reward, done, and info
        print("\n##### NEW ACTION #####")
        # Update the pod states based on the action
        if action == 0:  # No change in replicas
            print("Taking action 0")
            pass
        elif action == 1:  # Increase replicas
            print("Taking action +1")
            self.scale.update_replicas(1)
            self.current_replicas += 1
        elif action == 2:  # Decrease replicas
            print("Taking action -1")
            self.scale.update_replicas(-1)
            self.current_replicas -= 1

        # Get the new observation from Prometheus API
        # TODO wait 15 seconds to stabilise?
        print("Waiting 30 seconds to stabilise ...")
        time.sleep(30)
        new_observation = self._get_observation()

        # Calculate reward based on the new observation and previous response time
        # reward = -(self.alpha * int(new_observation[1] > self.previous_response_time) + self.current_replicas)
        # TODO modify so that time for productcatalogservice is below 100 ms
        SLA_RESP_TIME = 100 # 100 ms
        reward = -(self.alpha * int(new_observation[1] > SLA_RESP_TIME) + self.current_replicas)
        print("Reward: ", reward)

        # Update the previous response time for the next step
        # self.previous_response_time = new_observation[1]
        # Set done to False as the environment is not terminated in this example
        done = False

        # Set info to an empty dictionary
        info = {}

        # wait one minute before taking another action
        print("Waiting 30 seconds before taking next scaling action ...")
        time.sleep(30)

        return new_observation, reward, done, info

    def _get_observation(self):
        # Retrieve observation from Prometheus API, e.g., query response time, CPU usage, memory usage, and replicas
        observation = self.prom.get_results(self.queries)
        observation = np.array(observation)

        # Check for missing values in the observation
        if np.any(np.isnan(observation)):
            # Use the previous observation if any of the values are missing
            print("Attention! Missing values in results, substituting values of previous observation ...")
            observation = np.where(np.isnan(observation), self.current_observation, observation)

        # Update the current observation for the next step
        self.current_observation = observation

        return observation