import os
import sys
import json
import logging
# import tensorflow as tf
from stable_baselines3 import A2C
from stable_baselines3.common.logger import configure
from agent_env import GymEnvironment
from datetime import datetime
from datetime import timedelta
from Logger import LoggerWriter

MODEL = "A2C"
print(f"Using model {MODEL}.")
script_dir = os.path.dirname(os.path.abspath(__file__))

def create_directories():
    # Get the absolute path of the script directory
    models_dir = os.path.join(script_dir, f"models/{MODEL}")
    tf_logs_dir = os.path.join(script_dir, f"tf_logs/{MODEL}")
    pod_logs_dir = os.path.join(script_dir, f"pod_logs/{MODEL}")

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(tf_logs_dir):
        os.makedirs(tf_logs_dir)

    if not os.path.exists(pod_logs_dir):
        os.makedirs(pod_logs_dir)

    dirs = [models_dir, tf_logs_dir, pod_logs_dir]

    return dirs

def enable_logging(pod_logs_dir):
    t = datetime.now()
    t = t + timedelta(hours=2)
    timestamp = t.strftime("%Y_%m_%d_%H%M%S")
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
def setup_environment(alpha, cluster, url, name, namespace, minReplicas, maxReplicas):

    # Construct the absolute file path for queries.json
    queries_json_path = os.path.join(script_dir, "queries.json")

    q_file = open(queries_json_path, "r")
    data = json.load(q_file)

    # Define the hyperparameters for training
    # alpha = 100  # Your desired value for alpha
    # QUERIES FOR FRONTEND DEPLOYMENT
    _queries = data[cluster]
    queries = [
        _queries["q_pod_replicas"],
        _queries["q_request_duration"],
        _queries["q_cpu_usage"],
        _queries["q_memory_usage"],
    ]
    q_file.close()

    # Create an instance of GymEnvironment
    env = GymEnvironment(alpha, queries, url, name, namespace, minReplicas, maxReplicas)
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
        model = A2C.load(model_path, env=env, tensorboard_log=tf_logs_dir)
        # model = A2C.load(model_path, env=env)
    else:
        print("No existing models found. Starting from scratch.")
        logging.info("No existing models found. Starting from scratch.")
        # Create the A2C model
        model = A2C("MlpPolicy", env, verbose=1, tensorboard_log=tf_logs_dir)
        # model = A2C("MlpPolicy", env, verbose=1)

    # Add the file writer for TensorBoard logging
    # file_writer = tf.summary.create_file_writer(tf_logs_dir, model.policy.graph)
    # model.policy.set_tf_writer(file_writer)

    return model

def train_model(model, models_dir):
    TIMESTEPS = 10
    # training
    for i in range(1,10):
        print("Learning. Iteration: ", TIMESTEPS*i)
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=MODEL)
        # model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
        logging.info(f"Training iteration {i}, total_timesteps={TIMESTEPS*i}, saving model ...")
        print("Saving model ...")
        model.save(f"{models_dir}/{TIMESTEPS*i}")

    print("Training completed. Check performance on Tensorboard.")
    logging.info("Training completed. Check performance on Tensorboard.")

    return

if __name__ == "__main__":

    alpha = 100
    cluster = "gke"
    url = 'http://prometheus.istio-system.svc.cluster.local:9090'  # URL for Prometheus API
    name = "frontend" # deployment name
    namespace = "rl-agent" # namespace
    minReplicas = 1
    maxReplicas = 30

    dirs = create_directories()
    models_dir = dirs[0]
    tf_logs_dir = dirs[1]
    pod_logs_dir = dirs[2]
    logger = enable_logging(pod_logs_dir)
    env = setup_environment(alpha, cluster, url, name, namespace, minReplicas, maxReplicas)
    model = load_model(env, models_dir, tf_logs_dir)
    # new_logger = configure(tf_logs_dir, ["stdout", "csv", "tensorboard"])
    # model.set_logger(new_logger)
    train_model(model, models_dir)

    env.close()