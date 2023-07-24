import gym
from gym import spaces

from Scale import KubernetesEnvironment
from Query import PrometheusClient

import numpy as np
import time
import sys
import random

class GymEnvironment(gym.Env):

    def __init__(self, 
                 alpha, 
                 queries, 
                 url, 
                 name, 
                 namespace, 
                 minReplicas, 
                 maxReplicas,
                 rew_fun,
                 metrics):
        
        super(GymEnvironment, self).__init__()
        
        self.alpha = alpha

        self.queries = queries
        self.url = url
        self.prom = PrometheusClient(self.url)

        self.name = name
        self.namespace = namespace
        self.minReplicas = minReplicas
        self.maxReplicas = maxReplicas
        self.rew_fun = rew_fun
        self.scale = KubernetesEnvironment(self.name, self.namespace, self.minReplicas, self.maxReplicas)
        self.metrics = metrics
        self.curr_timestep = 0
        self.obs = {}
        self.reward = 0
        self.reward_sum = 0
        self.action_space = spaces.Discrete(3)  # Action space with 3 discrete actions: 1, 0, -1
        # self.observation_space = spaces.Box(low=0, high=np.inf, shape=(5,), dtype=np.float64)  # Observation space with 4 continuous elements: response time, CPU usage, memory usage, replicas
        # Create a Dict observation space
        # Needed because in this way we can easily select the metrics
        # in the state space from the command line when executing
        dict_obs = {}
        dict_obs.update({'rep': gym.spaces.Box(low=0, high=np.Inf, shape=(1,), dtype=np.float64)})
        for metric in self.metrics:
            dict_obs.update({metric: gym.spaces.Box(low=0, high=np.Inf, shape=(1,), dtype=np.float64)})
        self.observation_space = gym.spaces.Dict(dict_obs)
        
    
    def reset(self):
        # Reset the environment, e.g., initialize the pod states and retrieve initial observation
        # TODO do I need to reset the workload pattern?
        self.scale.reset_replicas() # Initialize current number of replicas as 1
        print("Waiting 120 seconds to stabilise after reset ...")
        time.sleep(120)
        self.reward_sum = 0
        self.obs = self._get_observation()  # Retrieve initial observation from Prometheus API
        self.current_replicas = self.obs['rep']
        self.reward_sum = 0
        # self.previous_response_time = self.current_observation[1]  # Initialize previous response time
        return self.obs

    def step(self, action):
        # Take a step in the environment based on the given action
        # Update the pod states, calculate reward, and return the new observation, reward, done, and info
        rep = self.current_replicas
        
        # Test, every 1000 timesteps, take random action
        if self.curr_timestep%1000 == 0:
            c = random.random()
            if c<=0.5: 
                action=1
                print(f"random selected action {action}")
            else: 
                action=2
                print(f"random selected action {action}")


        print("##### NEW ACTION #####")
        print(f"Taken action {action}")
        # Update the pod states based on the action
        if action == 0:  # No change in replicas
            # print(f"Taken action {action}, self.current_replicas: {self.current_replicas}")
            # Get the new observation from Prometheus API
            self.obs = self._get_observation()
            print("Waiting 30 seconds to stabilise ...")
            time.sleep(30)
            pass
        elif action == 1:  # Increase replicas
            print("Taking action +1")
            self.scale.update_replicas(1)
            print("Waiting 30 seconds to stabilise ...")
            time.sleep(30)
            # Get the new observation from Prometheus API
            self.obs = self._get_observation()
            rep = self.obs['rep']
            # print(f"Taking action +1, self.current_replicas: {self.current_replicas}")
        elif action == 2:  # Decrease replicas
            self.scale.update_replicas(-1)
            print("Waiting 30 seconds to stabilise ...")
            time.sleep(30)
            # Get the new observation from Prometheus API
            self.obs = self._get_observation()
            rep = self.obs['rep']
            # print(f"Taking action -1, self.current_replicas: {self.current_replicas}")
        print(f"Taken action {action}, updated rep: {rep}")

        self.current_replicas = rep

        # Calculate reward based on the new observation
        SLA_RESP_TIME = 5 # 5 ms
        resp_time = self.obs['p95']
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
            delta_t = resp_time-SLA_RESP_TIME
            perc = delta_t/SLA_RESP_TIME
            if perc>0:
                self.reward = -100*perc
                print(f"self.reward = -100*{perc} = {self.reward}")
            else:
                self.reward = 10*(10*((100/self.alpha) * perc + 1) + (self.maxReplicas/self.current_replicas))
                # self.reward = 1 + 100*(self.maxReplicas - self.current_replicas)
                print(f"self.reward = 10*({100/self.alpha}*{perc}+1) + ({self.maxReplicas/self.current_replicas}) = {self.reward}")
                # print(f"self.reward = 1 + 100*({self.maxReplicas - self.current_replicas}) = {self.reward}")
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
        elif self.rew_fun == "linear_3":
            # Quadratic reward function on exceeded time constraint
            if (self.current_replicas == self.maxReplicas and action == 1):
                self.reward = -100000
                print(f"self.reward = {self.reward}")
            elif (self.current_replicas == self.minReplicas and action == 2):
                self.reward = -100000
                print(f"self.reward = {self.reward}")
            else:
                delta_t = new_observation[1]-SLA_RESP_TIME
                if delta_t > 0:
                    # SLA violated, penalise a lot time exceeded
                    self.reward = -delta_t**2
                    print(f"self.reward = -delta_t**2 = {self.reward}")
                else:
                    # SLA satisfided, try to optimise number of replicas
                    self.reward = delta_t + (self.maxReplicas - self.current_replicas)
                    print(f"self.reward = {delta_t} + {self.maxReplicas} - {self.current_replicas} = {self.reward}")
        else:
            print("ERROR: your reward function selection is not valid.")
            sys.exit(1)

        # Set done to False as the environment is not terminated in this example
        done = False

        # update timestep
        self.curr_timestep += 1
        print(f"Current timestep: {self.curr_timestep}")
        # update reward
        self.reward_sum += self.reward
        # Set info to an empty dictionary
        info = {
            "total_reward": self.reward_sum
        }
        # wait one minute before taking another action
        # print("Waiting 30 seconds before taking next scaling action ...")
        # time.sleep(30)

        return self.obs, self.reward, done, info

    def _get_observation(self):
        # Retrieve observation from Prometheus API, e.g., query response time, CPU usage, memory usage, and replicas
        # observation = self.prom.get_results(self.queries, self.metrics)
        # print(f"\nObservation:\n{self.queries[0]}: {observation[0]};\n{self.queries[1]}: {observation[1]};\n{self.queries[2]}: {observation[2]};\n{self.queries[3]}: {observation[3]};\n{self.queries[4]}: {observation[4]};")
        # observation = {'rep': np.array(self.queries[f"q_rep"], dtype=np.float64).reshape(1,)}
        res = self.prom.query(self.queries['q_rep'])
        observation = {'rep': np.array(res, dtype=np.float64).reshape(1,)}
        
        for metric in self.metrics:
            res = self.prom.query(self.queries[f'q_{metric}'])
            observation.update( {metric: np.array(res, dtype=np.float64).reshape(1,)} )

        # Check for missing values in the observation
        for key in observation.keys():
            if np.isnan(observation[key]):
                # Use the previous observation if any of the values are missing
                print("Attention! Missing values in observation, substituting NaN with 0.0 ...")
                observation.update( {key: np.array(0.0, dtype=np.float64).reshape(1,)} )

        # Update the current observation for the next step
        # self.current_observation = observation
        print(f"Observation: {observation}")
        return observation