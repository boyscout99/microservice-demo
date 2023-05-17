import gym
from gym import spaces

# from Scale import KubernetesEnvironment
# from Query import PrometheusClient

import numpy as np
import time
import sys

class GymEnvironment(gym.Env):

    def __init__(self, 
                 alpha, 
                 queries, 
                 url, 
                 name, 
                 namespace, 
                 minReplicas, 
                 maxReplicas,
                 rew_fun):
        
        super(GymEnvironment, self).__init__()
        
        self.alpha = alpha

        self.queries = queries
        self.url = url
        # self.prom = PrometheusClient(self.url)

        self.name = name
        self.namespace = namespace
        self.minReplicas = minReplicas
        self.maxReplicas = maxReplicas
        self.rew_fun = rew_fun
        # self.scale = KubernetesEnvironment(self.name, self.namespace, self.minReplicas, self.maxReplicas)

        self.reward = 0
        self.action_space = spaces.Discrete(3)  # Action space with 3 discrete actions: 1, 0, -1
        # self.observation_space = spaces.Box(low=0, high=np.inf, shape=(5,), dtype=np.float64)  # Observation space with 4 continuous elements: response time, CPU usage, memory usage, replicas
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.float64)  # Observation space with 4 continuous elements: response time, CPU usage, memory usage, replicas

    def reset(self):
        # Reset the environment, e.g., initialize the pod states and retrieve initial observation
        # TODO do I need to reset the workload pattern?
        # self.scale.reset_replicas() # Initialize current number of replicas as 1
        # set replicas to 1:
        self.queries["q_pod_replicas"] = 1
        print("Waiting 1 seconds to stabilise after reset ...")
        time.sleep(1)

        self.current_observation = self._get_observation()  # Retrieve initial observation from Prometheus API
        self.current_replicas = self.current_observation[0]
        # self.previous_response_time = self.current_observation[1]  # Initialize previous response time
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
            # self.scale.update_replicas(1)
            self.queries["q_pod_replicas"] += 1
            if self.queries["q_pod_replicas"] > 30:
                print(f"Cannot have more than maxReplicas. Setting to {self.maxReplicas}.")
                self.queries["q_pod_replicas"] = 30

            # Consequences of the action on the environment
            # reduce CPU utilisation
            self.queries["q_cpu_usage"] = self.queries["q_cpu_usage"] - 50*self.queries["q_pod_replicas"]
            # reduce memory utilisation
            self.queries["q_memory_usage"] = self.queries["q_memory_usage"] - 0.5*self.queries["q_memory_usage"]*self.queries["q_pod_replicas"]
            # reduce service latency
            # self.queries["q_request_duration"] = 240 - 40*self.queries["q_pod_replicas"]

        elif action == 2:  # Decrease replicas
            print("Taking action -1")
            # self.scale.update_replicas(-1)
            self.queries["q_pod_replicas"] -= 1
            if self.queries["q_pod_replicas"] < 1:
                print(f"Cannot have less than minReplicas. Setting to {self.minReplicas}.")
                self.queries["q_pod_replicas"] = 1

            # Consequences of the action on the environment
            # increase CPU utilisation
            self.queries["q_cpu_usage"] = self.queries["q_cpu_usage"] + 0.5*self.queries["q_cpu_usage"]*self.queries["q_pod_replicas"]
            # increase memory utilisation
            self.queries["q_memory_usage"] = self.queries["q_memory_usage"] + 0.5*self.queries["q_memory_usage"]*self.queries["q_pod_replicas"]
            # increase service latency
            # self.queries["q_request_duration"] = 240 + 40*self.queries["q_pod_replicas"]
        
        self.current_replicas = self.queries["q_pod_replicas"]
        # get new observation
        new_observation = self._get_observation()

        # Calculate reward based on the new observation and previous response time
        SLA_RESP_TIME = 100 # 100 ms
        if self.rew_fun == "indicator":
            self.reward = -(self.alpha * int(new_observation[1] > SLA_RESP_TIME) + self.current_replicas)
        elif self.rew_fun == "quadratic":
            # Quadratic reward function on exceeded time constraint
            delta_t = new_observation[1]-SLA_RESP_TIME
            if delta_t > 0:
                # SLA violated, penalise a lot time exceeded
                # e.g. delta_t = 5ms, replicas = 30, reward = +5
                # e.g. delta_t = 50ms, replicas = 8, reward = -2492
                self.reward = -delta_t**2 + self.current_replicas
            else:
                # SLA satisfided, try to optimise number of replicas
                # self.reward = delta_t - self.alpha*self.current_replicas
                self.reward = -self.alpha*self.current_replicas
        elif self.rew_fun == "quad_cpu_thr":
            # Quadratic reward function on exceeded time constraint
            delta_t = new_observation[1]-SLA_RESP_TIME
            # penalise CPU throttling
            gamma = (new_observation[2]>100)*(100 - new_observation[2])
            if delta_t > 0:
                # SLA violated, penalise a lot time exceeded
                # e.g. delta_t = 5ms, replicas = 30, reward = +5
                # e.g. delta_t = 50ms, replicas = 8, reward = -2492
                self.reward = -delta_t**2 + self.current_replicas + gamma
            else:
                # SLA satisfided, try to optimise number of replicas
                self.reward = delta_t - self.alpha*self.current_replicas + gamma
        elif self.rew_fun == "linear_1":
            # Quadratic reward function on exceeded time constraint
            delta_t = new_observation[1]-SLA_RESP_TIME
            if delta_t > 0:
                # SLA violated, penalise a lot time exceeded
                self.reward = -100 + self.current_replicas
                print(f"self.reward = -100 +  {self.current_replicas} = {self.reward}")
            else:
                # SLA satisfided, try to optimise number of replicas
                self.reward = 100
                print(f"self.reward = {self.reward}")
        elif self.rew_fun == "linear_2":
            # Quadratic reward function on exceeded time constraint
            delta_t = new_observation[1]-SLA_RESP_TIME
            if delta_t > 0:
                # SLA violated, penalise a lot time exceeded
                self.reward = -100 + self.current_replicas
                print(f"self.reward = -100 +  {self.current_replicas} = {self.reward}")
            else:
                # SLA satisfided, try to optimise number of replicas
                self.reward = 100 - 3*self.current_replicas
                print(f"self.reward = {self.reward}")
        else:
            print("ERROR: your reward function selection is not valid.")
            sys.exit(1)

        # Update the previous response time for the next step
        # self.previous_response_time = new_observation[1]
        # Set done to False as the environment is not terminated in this example
        done = False

        # Set info to an empty dictionary
        info = {}

        # wait one minute before taking another action
        # print("Waiting 30 seconds before taking next scaling action ...")
        # time.sleep(30)

        return new_observation, self.reward, done, info

    def _get_observation(self):
        # Retrieve observation from Prometheus API, e.g., query response time, CPU usage, memory usage, and replicas
        # observation = self.prom.get_results(self.queries)
        observation = [
            self.queries["q_pod_replicas"],
            # self.queries["q_request_duration"],
            self.queries["q_cpu_usage"],
            self.queries["q_memory_usage"],
            self.queries["q_rps"]
        ]
        observation = np.array(observation)
        # Update the current observation for the next step
        self.current_observation = observation
        print(f"self.current_observation: {self.current_observation}")

        return observation