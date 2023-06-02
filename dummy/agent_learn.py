import os
import sys
import json
import logging
import importlib
import numpy as np
from agent_env import GymEnvironment
from datetime import datetime
from datetime import timedelta
from Logger import LoggerWriter
from ArgParser_learn import StringProcessor
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.callbacks import EvalCallback

class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=1):
        super(TensorboardCallback, self).__init__(verbose)
        self.episode_rewards = []
        self.ep_rew_mean = 0
        self.ep_rew_sum = 0

        self.replicas = 0
        self.t = 0
        self.cpu = 0
        self.mem = 0
        self.rps = 0

    def _on_rollout_start(self) -> None:
        self.episode_rewards = []
        self.replicas = 0
        self.t = 0
        self.cpu = 0
        self.mem = 0
        self.rps = 0
        print("ON ROLLOUT START")

    def _on_step(self) -> bool:
        # get current reward
        rewards = self.training_env.get_attr("reward")
        # append reward
        self.episode_rewards.extend(rewards)
        # get observations to log it at each step
        obs = self.training_env.get_attr("current_observation")
        self.replicas = obs[0][0]
        self.t = obs[0][1]
        self.rps = obs[0][2]
        self.cpu = obs[0][3]
        self.mem = obs[0][4]
        self.logger.record("rollout/replicas", self.replicas)
        self.logger.record("rollout/t", self.t)
        self.logger.record("rollout/rps", self.rps)
        self.logger.record("rollout/cpu", self.cpu)
        self.logger.record("rollout/mem", self.mem)
        print("ON STEP")
        return True

    def _on_rollout_end(self) -> None:
        # compute mean
        self.ep_rew_mean = np.mean(self.episode_rewards)
        # get total reward
        tot_reward = self.training_env.get_attr("reward_sum")
        self.ep_rew_sum = tot_reward[0]
        # log values
        self.logger.record("rollout/ep_rew_mean", self.ep_rew_mean)
        print("self.ep_rew_mean: ", self.ep_rew_mean)
        self.logger.record("rollout/ep_rew_sum", self.ep_rew_sum)
        print("self.ep_rew_sum: ", self.ep_rew_sum)
        # reset values
        self.ep_rew_sum = 0
        self.episode_rewards = []
        print("ON ROLLOUT END")


MODULE = "stable_baselines3"
t = datetime.now()
t = t + timedelta(hours=2) # UTC+2
timestamp = t.strftime("%Y_%m_%d_%H%M%S")

# Read arguments
processor = StringProcessor()
DEPLOYMENT, NAMESPACE, CLUSTER, MODEL, REWARD_FUNCTION, LEARNING_RATE = processor.parse_args() # read namespace and model
print(f"deployment {DEPLOYMENT}, namespace {NAMESPACE}, cluster {CLUSTER}, model {MODEL}, reward function {REWARD_FUNCTION}, learning rate {LEARNING_RATE}.")

module = importlib.import_module(MODULE) # import stable_baselines3
model_attr = getattr(module, MODEL) # e.g. from stable_baselines3 import A2C

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

def create_directories():
    # create the necessary directories
    models_dir = os.path.join(script_dir, f"models/{NAMESPACE}/{MODEL}/{timestamp}")
    tf_logs_dir = os.path.join(script_dir, f"tf_logs/{NAMESPACE}/{MODEL}/{timestamp}")
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
                      data):

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
                         data)
    # set default state
    env.reset()

    return env

def load_model(env, models_dir, tf_logs_dir):
    # Check for existing models and load the last saved model if available
    existing_models = [f for f in os.listdir(models_dir)]
    if existing_models:
        # Sort models by their names to get the last saved model
        existing_models.sort()
        last_saved_model = existing_models[-1]
        model_path = os.path.join(models_dir, last_saved_model)
        print(f"Loading last saved model: {model_path}")
        logging.info(f"Loading last saved model: {model_path}")
        model = model_attr.load(model_path, env=env, tensorboard_log=tf_logs_dir)
    else:
        print("No existing models found. Starting from scratch.")
        logging.info("No existing models found. Starting from scratch.")
        # Create the model
        if MODEL == "A2C":
            model = model_attr("MlpPolicy", 
                            env, 
                            learning_rate=float(LEARNING_RATE),
                            verbose=1,
                            n_steps=5, 
                            gamma=0.99, 
                            gae_lambda=1.0, 
                            ent_coef=0.0, 
                            vf_coef=0.5, 
                            max_grad_norm=0.5, 
                            rms_prop_eps=1e-05,
                            tensorboard_log=tf_logs_dir)
        elif MODEL == "DQN":
            model = model_attr("MlpPolicy", 
                            env, 
                            learning_rate=float(LEARNING_RATE),
                            learning_starts=0,
                            target_update_interval=2,
                            train_freq=1,
                            verbose=2, 
                            tensorboard_log=tf_logs_dir)

    return model

def train_model(model, models_dir, timesteps, episodes, callbacks):
    # training
    for i in range(1,episodes):
        print("Learning. Iteration: ", timesteps*i)
        # model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=MODEL, log_interval=2, callback=rewards_callback)
        model.learn(total_timesteps=timesteps, 
                    tb_log_name=MODEL, 
                    log_interval=2, 
                    callback=callbacks)
        # model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
        logging.info(f"Training iteration {i}, total_timesteps={TIMESTEPS*i}, saving model ...")
        print("Saving model ...")
        model.save(f"{models_dir}/{TIMESTEPS*i}")
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
    maxReplicas = 7
    rew_fun = REWARD_FUNCTION
    # define alpha based on the selected reward function
    if rew_fun == "indicator": alpha = 100
    elif rew_fun == "quadratic": alpha = 2
    elif rew_fun == "quad_cpu_thr": alpha = 2
    else: alpha = 1

    TIMESTEPS = 1000
    EPISODES = 10

    dirs = create_directories()
    models_dir = dirs[0]
    tf_logs_dir = dirs[1]
    pod_logs_dir = dirs[2]
    logger = enable_logging(pod_logs_dir)

    # copy data
    data_json_path = os.path.join(script_dir, "sample.json")
    # read made up data
    d_file = open(data_json_path, "r")
    d = json.load(d_file)
    data = d
    print(f"data:\n{data}")
    d_file.close()

    env = setup_environment(alpha, 
                            cluster, 
                            url, 
                            name, 
                            namespace, 
                            minReplicas, 
                            maxReplicas, 
                            rew_fun,
                            data)
    env = Monitor(env, tf_logs_dir)
    model = load_model(env, models_dir, tf_logs_dir)

    # create callbacks
    rewards_callback = TensorboardCallback()
    # eval_callback = EvalCallback(env, 
    #                             best_model_save_path=models_dir,
    #                             log_path=models_dir, 
    #                             eval_freq=1,
    #                             deterministic=True, 
    #                             render=False,
    #                             verbose=1)
    callbacks = [rewards_callback]
    # train the model
    train_model(model, 
                models_dir, 
                TIMESTEPS,
                EPISODES,
                callbacks)
    # close the environment on completion
    env.close()