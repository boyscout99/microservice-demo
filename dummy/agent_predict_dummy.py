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
from ArgParser_predict import StringProcessor
from stable_baselines3.common.monitor import Monitor

MODULE = "stable_baselines3"
t = datetime.now()
t = t + timedelta(hours=2) # UTC+2
timestamp = t.strftime("%Y_%m_%d_%H%M%S")

# Read arguments
processor = StringProcessor()
DEPLOYMENT, NAMESPACE, CLUSTER, MODEL, REWARD_FUN, MODEL_DIR = processor.parse_args() # read namespace and model
print(f"deployment {DEPLOYMENT}, namespace {NAMESPACE}, cluster {CLUSTER}, model {MODEL}, reward function {REWARD_FUN}, model_dir {MODEL_DIR}")

module = importlib.import_module(MODULE) # import stable_baselines3
model_attr = getattr(module, MODEL) # e.g. from stable_baselines3 import A2C

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

def create_directories():
    # create the necessary directories
    tf_logs_dir = os.path.join(script_dir, f"tf_logs/predict/{NAMESPACE}/{MODEL}/{timestamp}")
    pod_logs_dir = os.path.join(script_dir, f"pod_logs/{NAMESPACE}/{MODEL}")

    if not os.path.exists(tf_logs_dir):
        os.makedirs(tf_logs_dir)

    if not os.path.exists(pod_logs_dir):
        os.makedirs(pod_logs_dir)

    dirs = [tf_logs_dir, pod_logs_dir]

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
    logger = logging.getLogger(__name__)

    # Redirect console output to logger
    sys.stdout = LoggerWriter(logger.info)
    sys.stderr = LoggerWriter(logger.error)

    return logger

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

def load_selected_model(env, model_path, tf_logs_dir):
    # Load the selected model
    try:
        print(f"Loading selected model: {model_path}")
        logging.info(f"Loading selected model: {model_path}")
        model = model_attr.load(model_path, env=env, tensorboard_log=tf_logs_dir)
    except:
        print("No existing models found. Please load a valid model.")
        logging.info("No existing models found. Please load a valid model.")

    return model

if __name__ == "__main__":

    # cluster = "minikube"
    cluster = CLUSTER
    url = 'http://prometheus.istio-system.svc.cluster.local:9090'  # URL for Prometheus API
    # name = "frontend" # deployment name
    name = DEPLOYMENT
    #  namespace = "rl-agent" # namespace
    namespace = NAMESPACE
    minReplicas = 1
    maxReplicas = 30
    rew_fun = REWARD_FUN
    # define alpha based on the selected reward function
    if rew_fun == "indicator": alpha = 100
    elif rew_fun == "quadratic": alpha = 2
    elif rew_fun == "quad_cpu_thr": alpha = 2
    else: alpha = 1

    TIMESTEPS = 1000
    EPISODES = 10

    dirs = create_directories()
    tf_logs_dir = dirs[0]
    pod_logs_dir = dirs[1]
    logger = enable_logging(pod_logs_dir)

    # copy data
    data_json_path = os.path.join(script_dir, "data_3.json")
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
    MODEL_DIR = os.path.join(script_dir, MODEL_DIR)
    model = load_selected_model(env, MODEL_DIR, tf_logs_dir)

    obs = env.reset()
    # Take actions in a loop
    # while True:
    for i in range(1, 500):
        # Get the recommended action from the model
        action, _states = model.predict(obs)
        # Take the recommended action in the environment
        obs, reward, done, info = env.step(action)
        if done:
            break

    # close the environment on completion
    env.close()