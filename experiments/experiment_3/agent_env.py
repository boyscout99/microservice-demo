import gym
from gym import spaces

# from Scale import KubernetesEnvironment
# from Query import PrometheusClient

import numpy as np
import time
import sys
from get_metrics import GetMetrics

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
                 data,
                 workload,
                 metrics):
        
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
        self.data = data
        self.metrics = metrics
        # self.scale = KubernetesEnvironment(self.name, self.namespace, self.minReplicas, self.maxReplicas)
        self.workload = workload
        self.reward = 0
        self.reward_sum = 0
        self.curr_timestep = 0
        self.obs = {}
        self.action_space = spaces.Discrete(3)  # Action space with 3 discrete actions: 1, 0, -1
        # self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,)) # Continuous action space 
        # self.observation_space = spaces.Box(low=0, high=np.inf, shape=(5,), dtype=np.float64)  # Observation space with 5 continuous elements: replicas, p90 latency, response time, CPU usage, memory usage
        # Create a Dict observation space
        dict_obs = {}
        for metric in self.metrics:
            dict_obs.update({metric: gym.spaces.Box(low=0, high=np.Inf, shape=(1,), dtype=np.float64)})
        self.observation_space = gym.spaces.Dict(dict_obs)
        # self.observation_space = spaces.Box(low=0, high=np.inf, shape=(4,), dtype=np.float64)
        # self.observation_space = spaces.Box(low=0, high=np.inf, shape=(3,), dtype=np.float64)  # Observation space with 3 continuous elements: replicas, p90 latency, response time
        
    def reset(self):
        # Reset the environment, e.g., initialize the pod states and retrieve initial observation
        # TODO do I need to reset the workload pattern?
        # self.scale.reset_replicas() # Initialize current number of replicas as 1
        # set replicas to 1:
        # self.queries["q_pod_replicas"] = 1
        print("Waiting 1 seconds to stabilise after reset ...")
        time.sleep(0.1)
        # reset queries to initial state
        # set current timestep to 0
        self.curr_timestep = 0
        # set number of replicas to 1
        self.queries["q_rep"] = 1
        # get value of workload at t_0 self.workload[0] and approximate other data
        dict_app_metrics = GetMetrics(self.data, self.metrics).get_metrics_approx(1, self.workload[self.curr_timestep])
        for metric in self.metrics:
            self.queries[f"q_{metric}"] = dict_app_metrics[metric]
        # retreive observation
        self.obs = self._get_observation()
        self.current_replicas = self.obs['rep']
        self.reward_sum = 0
        # self.previous_response_time = self.current_observation[1]  # Initialize previous response time
        return self.obs

    def step(self, action):
        # Take a step in the environment based on the given action
        # Update the pod states, calculate reward, and return the new observation, reward, done, and info

        # rename variables to have shorter and more practical names
        # rep = self.queries["q_pod_replicas"]
        # t = self.queries["q_request_duration"]
        # rps = self.queries["q_rps"]
        # cpu = self.queries["q_cpu_usage"]
        # mem = self.queries["q_memory_usage"]
        rep = self.current_replicas

        # print(f"action: {action}")
        # thresholds = [-0.33, 0.33]
        # if action < thresholds[0]: action = 0
        # elif action > thresholds[1]: action = 1
        # else: action = 2

        print("##### NEW ACTION #####")
        # Update the pod states based on the action
        if action == 0:  # No change in replicas
            
            print("Taking action 0")
            print(f"workload[{self.curr_timestep}] = {self.workload[self.curr_timestep]}")
            dict_app_metrics = GetMetrics(self.data, self.metrics).get_metrics_approx(rep, self.workload[self.curr_timestep])
            print(dict_app_metrics)
            pass
        elif action == 1:  # Increase replicas
            print("Taking action +1")
            print(f"workload[{self.curr_timestep}] = {self.workload[self.curr_timestep]}")
            # self.scale.update_replicas(1)
            rep += 1
            if rep > self.maxReplicas:
                print(f"Cannot have more than maxReplicas. Setting to {self.maxReplicas}.")
                rep = self.maxReplicas
                # Consequences of action on environment
                dict_app_metrics = GetMetrics(self.data, self.metrics).get_metrics_approx(rep, self.workload[self.curr_timestep])
                print(dict_app_metrics)
            else:
                # Consequences of action on environment
                dict_app_metrics = GetMetrics(self.data, self.metrics).get_metrics_approx(rep, self.workload[self.curr_timestep])
                print(dict_app_metrics)

        elif action == 2:  # Decrease replicas
            print("Taking action -1")
            print(f"workload[{self.curr_timestep}] = {self.workload[self.curr_timestep]}")
            # self.scale.update_replicas(-1)
            rep -= 1
            if rep < self.minReplicas:
                print(f"Cannot have less than minReplicas. Setting to {self.minReplicas}.")
                rep = self.minReplicas
                # Consequences of action on environment
                dict_app_metrics = GetMetrics(self.data, self.metrics).get_metrics_approx(rep, self.workload[self.curr_timestep])
                print(dict_app_metrics)
            else:
                # Consequences of action on environment
                dict_app_metrics = GetMetrics(self.data, self.metrics).get_metrics_approx(rep, self.workload[self.curr_timestep])
                print(dict_app_metrics)

        self.current_replicas = rep
        # reassign values
        self.queries[f"q_rep"] = self.current_replicas
        for metric in self.metrics:
            self.queries[f"q_{metric}"] = dict_app_metrics[metric]

        # waiting environment to stabilise
        # time.sleep(1)
        # get new observation
        # new_observation = self._get_observation()
        self.obs = self._get_observation()

        # Calculate reward based on the new observation
        SLA_RESP_TIME = 5 # 100 ms
        resp_time = self.obs['p95']
        if self.rew_fun == "indicator":
            self.reward = -(self.alpha * int(self.obs['p95'] > SLA_RESP_TIME) + self.current_replicas)
        elif self.rew_fun == "quadratic":
            # Quadratic reward function on exceeded time constraint
            delta_t = self.obs['p95']-SLA_RESP_TIME
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
            delta_t = self.obs['p95']-SLA_RESP_TIME
            # penalise CPU throttling
            gamma = (self.obs['cpu']>100)*(100 - self.obs['cpu'])
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
                self.reward = 10*((100/self.alpha) * perc + 1) + (self.maxReplicas/self.current_replicas)
                print(f"self.reward = 10*({100/self.alpha}*{perc}+1) + ({self.maxReplicas/self.current_replicas}) = {self.reward}")
        elif self.rew_fun == "linear_2":
            delta_t = self.obs['p95']-SLA_RESP_TIME
            if delta_t > 0:
                # SLA violated, penalise a lot time exceeded
                self.reward = -delta_t
                print(f"self.reward = -{delta_t} = {self.reward}")
            else:
                # SLA satisfided, try to optimise number of replicas
                self.reward = 10*(self.maxReplicas - self.current_replicas)
                print(f"self.reward = {self.maxReplicas} - {self.current_replicas} = {self.reward}")
        elif self.rew_fun == "linear_3":
            # Quadratic reward function on exceeded time constraint
            # if (self.current_replicas == self.maxReplicas and action == 1):
            #     self.reward = -10000
            #     print(f"self.reward = {self.reward}")
            # elif (self.current_replicas == self.minReplicas and action == 2):
            #     self.reward = -10000
            #     print(f"self.reward = {self.reward}")
            # else:
                delta_t = self.obs['p95']-SLA_RESP_TIME
                if delta_t > 0:
                    # SLA violated, penalise a lot time exceeded
                    self.reward = -delta_t**2
                    print(f"self.reward = -{delta_t**2} = {self.reward}")
                else:
                    # SLA satisfided, try to optimise number of replicas
                    self.reward = 1 - (self.current_replicas/self.maxReplicas)# + (self.maxReplicas - self.current_replicas)
                    print(f"self.reward = 1 - {self.current_replicas/self.maxReplicas} = {self.reward}")
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
        # observation = self.prom.get_results(self.queries)
        observation = {'rep': np.array(self.queries[f"q_rep"], dtype=np.float64)}
        for metric in self.metrics:
            observation.update( {metric: np.array(self.queries[f"q_{metric}"], dtype=np.float64)} )

        print(f"observation: {observation}")

        return observation