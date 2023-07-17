"""
This code is to train the agent.
"""
import os
import sys
import json
import logging
import importlib
import numpy as np
import matplotlib.pyplot as plt
from agent_env import GymEnvironment
from datetime import datetime
from datetime import timedelta
from settings.Logger import LoggerWriter
from settings.ArgParser_learn import StringProcessor
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import BaseCallback
from workload_patterns_gen import WorkloadGenerator
from gym.wrappers import FlattenObservation
from stable_baselines3.common.env_checker import check_env

BEST_MODEL = -np.Inf
MAX_REWARD = -np.Inf
CURRENT_EPISODE = 1

MODULE = "stable_baselines3"
t = datetime.now()
t = t + timedelta(hours=2) # UTC+2
timestamp = t.strftime("%Y_%m_%d_%H%M%S")

# Read command line arguments
processor = StringProcessor()
DEPLOYMENT, NAMESPACE, CLUSTER, MODEL, REWARD_FUNCTION, LEARNING_RATE, METRICS = processor.parse_args() # read namespace and model
print(f"deployment {DEPLOYMENT}, namespace {NAMESPACE}, cluster {CLUSTER}, model {MODEL}, reward function {REWARD_FUNCTION}, learning rate {LEARNING_RATE}, metrics {METRICS}.")

module = importlib.import_module(MODULE) # import stable_baselines3
model_attr = getattr(module, MODEL) # e.g. from stable_baselines3 import A2C

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=1):
        super(TensorboardCallback, self).__init__(verbose)
        self.episode_rewards = []
        self.ep_rew_sum = 0
        self.train_all_rew = []
        incl_metrics = ""
        for metric in METRICS:
            incl_metrics += '_' + metric
        self.save_path = os.path.join(script_dir, f"models/{NAMESPACE}/{MODEL}/{timestamp}_{incl_metrics}")
        
    def _on_rollout_start(self) -> None:
        self.episode_rewards = []       
        print("ON ROLLOUT START")

    def _on_step(self) -> bool:
        # get current reward
        reward = self.training_env.get_attr("reward")
        # append reward
        self.episode_rewards.extend(reward)
        # get observations to log it at each step
        obs = self.training_env.get_attr("obs")
        # print(f"Obs from callback: {obs}")
        replicas = obs[0]['rep']
        self.logger.record("rollout/replicas", float(replicas))
        self.logger.record("rollout/rewards", reward[0])
        # print(type(float(replicas)))

        global METRICS
        for metric in METRICS:
            # print(f"logging to tb {metric}: {obs[0][metric]}")
            self.logger.record(f"rollout/{metric}", float(obs[0][metric]))
            # print(f"self.logger.record(f\"rollout/{metric}\", {float(obs[0][metric])})")
            # print(type(float(obs[0][metric])))
        print("ON STEP")
        return True

    def _on_rollout_end(self) -> None:
        self.train_all_rew.extend(self.episode_rewards)
        # get total reward
        tot_reward = self.training_env.get_attr("reward_sum")
        self.ep_rew_sum = tot_reward[0]
        # log values
        # self.logger.record("rollout/ep_rew_mean", self.ep_rew_mean)
        # print("self.ep_rew_mean: ", self.ep_rew_mean)
        self.logger.record("rollout/ep_rew_sum", self.ep_rew_sum)
        # print("self.ep_rew_sum: ", self.ep_rew_sum)
        # reset values
        self.ep_rew_sum = 0
        self.episode_rewards = []
        print("ON ROLLOUT END")
    
    def _on_training_end(self) -> None:
        """
        This event is triggered before exiting the `learn()` method.
        """
        # TODO 
        # Get best model based on number of maximum rewards.
        # Get maximum of the episode. Count how many time it was reached.
        global BEST_MODEL
        global MAX_REWARD
        global CURRENT_EPISODE
        print("ON TRAINING END")
        print(f"self.train_all_rew[len: {len(self.train_all_rew)}]: {self.train_all_rew}")
        # tmp_max_reward = max(self.train_all_rew)
        # Take Gt, the sum of all rewards in the episode
        tmp_max_reward = sum(self.train_all_rew)
        print(f"tmp_max_reward: {tmp_max_reward}")
        if tmp_max_reward > MAX_REWARD: 
            MAX_REWARD = tmp_max_reward
            print(f"New MAX_REWARD: {MAX_REWARD}")
            print(f"Saving new best model to {self.save_path}")
            self.model.save(os.path.join(self.save_path, f"best_ep{CURRENT_EPISODE}"))

        self.train_all_rew = []
        pass

def create_directories():
    # create the necessary directories
    incl_metrics = ""
    for metric in METRICS:
        incl_metrics += '_' + metric

    tf_logs_dir = os.path.join(script_dir, f"tf_logs/{NAMESPACE}/{MODEL}/predict/{timestamp}_{incl_metrics}")
    pod_logs_dir = os.path.join(script_dir, f"pod_logs/{NAMESPACE}/{MODEL}/predict/")

    if not os.path.exists(tf_logs_dir):
        os.makedirs(tf_logs_dir)

    if not os.path.exists(pod_logs_dir):
        os.makedirs(pod_logs_dir)

    dirs = [tf_logs_dir, pod_logs_dir]

    return dirs

def enable_logging(pod_logs_dir):
    pod_log_file = os.path.join(pod_logs_dir, f"{MODEL}_predict_{timestamp}.log")
    # logging.basicConfig(filename=pod_log_file, level=logging.DEBUG)  # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format=f"{timestamp} [%(levelname)s] %(message)s",
        filename=pod_log_file
    )
    
    # Define a logger
    my_logger = logging.getLogger(__name__)

    # Redirect console output to logger
    sys.stdout = LoggerWriter(my_logger.info)
    sys.stderr = LoggerWriter(my_logger.error)

    return my_logger

### SET UP THE ENVIRONMENT ###
def setup_environment(alpha, 
                      cluster, 
                      url, 
                      name, 
                      namespace, 
                      minReplicas, 
                      maxReplicas,
                      rew_fun,
                      data,
                      workload,
                      metrics):

    # Construct the absolute file path for queries.json
    queries_json_path = os.path.join(script_dir, "queries.json")
    q_file = open(queries_json_path, "r")
    q = json.load(q_file)
    queries = q[cluster][name][namespace]
    q_file.close()

    # Create an instance of GymEnvironment
    env = GymEnvironment(alpha, 
                         queries, 
                         url, 
                         name, 
                         namespace, 
                         minReplicas, 
                         maxReplicas, 
                         rew_fun,
                         data,
                         workload,
                         metrics)
    # set default state
    env.reset()

    return env

def load_selected_model(env, model_path, tf_logs_dir):
    # Load the selected model
    print(f"model_path: {model_path}")
    try:
        model = model_attr.load(model_path, env=env, tensorboard_log=tf_logs_dir)
        logging.info(f"Loading selected model: {model_path}")
    except Exception as e:
        logging.info(f"Error: {e}")
        return None

    return model

def flatten_observation(observation):
    if isinstance(observation, dict):
        # If observation is a dictionary, flatten its values recursively
        print("A dictionary!")
        flattened = [flatten_observation(value) for value in observation.values()]
        print(f"flattened: {flattened}")
        return flattened #np.array([element.item() for element in flattened])
    elif isinstance(observation, tuple):
        # If observation is a tuple, flatten its elements recursively
        flattened = [flatten_observation(element) for element in observation]
        return np.concatenate(flattened)
    else:
        # If observation is a ndarray, return it as is
        return np.asarray(observation)


if __name__ == "__main__":

    # cluster = "minikube"
    cluster = CLUSTER
    url = 'http://prometheus.istio-system.svc.cluster.local:9090'  # URL for Prometheus API
    name = DEPLOYMENT
    namespace = NAMESPACE
    minReplicas = 1
    maxReplicas = 15
    rew_fun = REWARD_FUNCTION
    # define alpha based on the selected reward function
    if rew_fun == "indicator": alpha = 100
    elif rew_fun == "quadratic": alpha = 2
    elif rew_fun == "quad_cpu_thr": alpha = 2
    elif rew_fun == "linear_1": alpha = 15 # 15% of optimisation gap
    else: alpha = 1

    TIMESTEPS = 300

    # Generate workload
    # This signal must be passed to the environment for the observation
    # set steps=1 for a constant load of minRPS
    _, rps_signal = WorkloadGenerator.decr_step_function(timesteps=TIMESTEPS+1, 
                                                 minRPS=1500,
                                                 maxRPS=1500,
                                                 steps=1)
    # plt.plot(_, rps_signal)
    # plt.title(f"Workload signal, {len(rps_signal)} timesteps")
    # plt.show()

    # Generate directories
    dirs = create_directories()
    tf_logs_dir = dirs[0]
    pod_logs_dir = dirs[1]
    logger = enable_logging(pod_logs_dir)

    # Copy samples for synthetic traffic
    data_json_path = os.path.join(script_dir, "exp3_sorted_samples.json")
    d_file = open(data_json_path, "r")
    data = json.load(d_file)
    # print(f"Data samples:\n{data}")
    d_file.close()

    # Generate environment
    env = setup_environment(alpha, 
                            cluster, 
                            url, 
                            name, 
                            namespace, 
                            minReplicas, 
                            maxReplicas, 
                            rew_fun,
                            data,
                            rps_signal,
                            METRICS) # adding workload
    print("Checking the environment ...")
    # check_env(env)
    env = Monitor(env, tf_logs_dir)
    # create callbacks
    rewards_callback = TensorboardCallback()
    callbacks = [rewards_callback]

    MODEL_DIR = 'models/rl-agent-2/A2C/2023_07_17_190302__p95_CPU_rps_mem/best_ep73.zip'
    MODEL_DIR = os.path.join(script_dir, MODEL_DIR)
    print(f"model dir: {MODEL_DIR}")
    model = load_selected_model(env, MODEL_DIR, tf_logs_dir)
    # model.set_callback(rewards_callback)

    obs = env.reset()
    # initialise logs
    logs = {'rep' : [0]}
    for metric in METRICS:
        logs[metric] = [0]
    # obs = flatten_observation(obs)
    # print(f"Flattened observation: {obs}")
    # Take actions in a loop
    # while True:
    for i in range(1, TIMESTEPS):
        # Get the recommended action from the model
        # print(f"Timestep: {i}")
        # print(obs)
        action, _states = model.predict(obs, deterministic=True)
        # Take the recommended action in the environment
        obs, reward, done, info = env.step(action)
        # print(f"obs: {obs}, reward: {reward}, done: {done}, info: {info}")
        for key in obs.keys():
            logs[key].append(round(float(obs[key]),2))
        if done:
            break

    # Remove first element from each key
    for key in logs.keys(): 
        logs[key].pop(0)
    # Compute mean and std of replicas
    mean_rep = np.mean(logs['rep'])
    std_rep = np.std(logs['rep'])
    # Compute number of SLA violations
    violations = sum(i>5 for i in logs['p95'])/len(logs['p95']) # df_p95[df_p95['Value']>5]['Value'].count()/df_p95['Value'].count()
    # print(f"logs: {logs}")
    Gt = info['total_reward']
    print(f"Total reward: {Gt}")
    print(f"Replicas: mean: {mean_rep}, std: {std_rep}")
    print(f"SLA violations: {violations*100}%")
    # close the environment on completion
    env.close()