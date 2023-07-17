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
# from stable_baselines3.common.buffers import ReplayBuffer
# from stable_baselines3.common.vec_env import DummyVecEnv
# from stable_baselines3.common.callbacks import EvalCallback
from workload_patterns_gen import WorkloadGenerator
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
        # sum_positives = sum(1 for element in self.train_all_rew if element == MAX_REWARD)
        # print("Number of maximum rewards in the episode: ", sum_positives)
        # if sum_positives > BEST_MODEL:
        #     # update the new best model
        #     BEST_MODEL = sum_positives
        #     # save the new best model
        #     print(f"Saving new best model to {self.save_path}")
        #     self.model.save(os.path.join(self.save_path, f"best_ep{CURRENT_EPISODE}"))
        self.train_all_rew = []
        pass

def create_directories():
    # create the necessary directories
    incl_metrics = ""
    for metric in METRICS:
        incl_metrics += '_' + metric
    models_dir = os.path.join(script_dir, f"models/{NAMESPACE}/{MODEL}/{timestamp}_{incl_metrics}")
    tf_logs_dir = os.path.join(script_dir, f"tf_logs/{NAMESPACE}/{MODEL}/{timestamp}_{incl_metrics}")
    pod_logs_dir = os.path.join(script_dir, f"pod_logs/{NAMESPACE}/{MODEL}")

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(tf_logs_dir):
        os.makedirs(tf_logs_dir)

    if not os.path.exists(pod_logs_dir):
        os.makedirs(pod_logs_dir)

    dirs = [models_dir, tf_logs_dir, pod_logs_dir]

    return dirs

def enable_logging(pod_logs_dir):
    pod_log_file = os.path.join(pod_logs_dir, f"{MODEL}_learn_{timestamp}.log")
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
    # QUERIES FOR FRONTEND DEPLOYMENT
    # _queries = data[cluster][name][namespace]
    queries = q[cluster][name][namespace]
    # queries = [
    #     _queries["q_pod_replicas"],
    #     _queries["q_request_duration"],
    #     _queries["q_cpu_usage"],
    #     _queries["q_memory_usage"],
    #     _queries["q_rps"]
    # ]
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

def load_model(env, models_dir, tf_logs_dir):
    # Check for existing models and load the last saved model if available
    # existing_models = [f for f in os.listdir(models_dir)]
    # if existing_models:
    #     # Sort models by their names to get the last saved model
    #     existing_models.sort()
    #     last_saved_model = existing_models[-1]
    #     model_path = os.path.join(models_dir, last_saved_model)
    #     print(f"Loading last saved model: {model_path}")
    #     logging.info(f"Loading last saved model: {model_path}")
    #     model = model_attr.load(model_path, env=env, tensorboard_log=tf_logs_dir)
    # else:
    #     print("No existing models found. Starting from scratch.")
    #     logging.info("No existing models found. Starting from scratch.")
    #     # Create the model
    if MODEL == "A2C":
        model = model_attr(
            "MultiInputPolicy", 
            env, 
            learning_rate=float(LEARNING_RATE),
            verbose=1,
            n_steps=3, 
            gamma=0.95,
            gae_lambda=1.0, 
            ent_coef=0.0, 
            vf_coef=0.5, 
            max_grad_norm=0.5, 
            rms_prop_eps=1e-05,
            tensorboard_log=tf_logs_dir
            )
    elif MODEL == "DQN":
        model = model_attr(
            "MultiInputPolicy", 
            env, 
            learning_rate=float(LEARNING_RATE),
            learning_starts=0,
            target_update_interval=2,
            train_freq=1,
            verbose=1, 
            tensorboard_log=tf_logs_dir
            )
    elif MODEL == "DDPG":
        model = model_attr(
            "MultiInputPolicy",
            env,
            verbose=2,
            learning_rate=float(LEARNING_RATE),
            tensorboard_log=tf_logs_dir
        )
    # print("No existing models found. Starting from scratch.")
    # logging.info("No existing models found. Starting from scratch.")

    return model

def train_model(model, models_dir, timesteps, episodes, callbacks):
    # training
    for i in range(0,episodes):
        print("Learning. Iteration: ", timesteps*i)
        # model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=MODEL, log_interval=2, callback=rewards_callback)
        model.learn(total_timesteps=timesteps, 
                    tb_log_name=MODEL, 
                    log_interval=1, 
                    callback=callbacks)
        # model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
        logging.info(f"Training iteration {i}, total_timesteps={TIMESTEPS*i}, saving model ...")
        global CURRENT_EPISODE 
        CURRENT_EPISODE += 1
        # print("Saving model ...")
        # model.save(f"{models_dir}/{TIMESTEPS*i}")
        # env.reset()

    print("Training completed. Check performance on Tensorboard.")
    logging.info("Training completed. Check performance on Tensorboard.")

    return

if __name__ == "__main__":

    # cluster = "minikube"
    cluster = CLUSTER
    url = 'http://prometheus.istio-system.svc.cluster.local:9090'  # URL for Prometheus API
    # name = "frontend" # deployment name
    name = DEPLOYMENT
    #  namespace = "rl-agent" # namespace
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
    EPISODES = 300

    # Generate workload
    # This signal must be passed to the environment for the observation
    # set steps=1 for a constant load of minRPS
    _, rps_signal = WorkloadGenerator.decr_step_function(timesteps=TIMESTEPS+1, 
                                                 minRPS=150,
                                                 maxRPS=1500,
                                                 steps=4)
    # plt.plot(_, rps_signal)
    # plt.title(f"Workload signal, {len(rps_signal)} timesteps")
    # plt.show()

    # Generate directories
    dirs = create_directories()
    models_dir = dirs[0]
    tf_logs_dir = dirs[1]
    pod_logs_dir = dirs[2]
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
    model = load_model(env, models_dir, tf_logs_dir)
    print(f"Model prameters: {model.get_parameters}")
    print(f"Model policy: {model.policy}")

    # create callbacks
    rewards_callback = TensorboardCallback()
    callbacks = [rewards_callback]
    # Create a replay buffer
    # replay_buffer = ReplayBuffer(buffer_size, obs_space, action_space)
    # model.collect_rollouts(env, callbacks, train_freq=5, replay_buffer=replay_buffer)
    # train the model
    train_model(model, 
                models_dir, 
                TIMESTEPS,
                EPISODES,
                callbacks)
    # close the environment on completion
    env.close()