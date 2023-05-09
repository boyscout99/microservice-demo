import os
import sys
import json
import logging
import importlib
from agent_env import GymEnvironment
from datetime import datetime
from datetime import timedelta
from Logger import LoggerWriter
from ArgParser import StringProcessor
from stable_baselines3.common.monitor import Monitor

MODULE = "stable_baselines3"

# Read arguments
processor = StringProcessor()
NAMESPACE, CLUSTER, MODEL, REWARD_FUNCTION = processor.parse_args() # read namespace and model
print(f"namespace {NAMESPACE}, cluster {CLUSTER}, model {MODEL}, reward function {REWARD_FUNCTION}.")

module = importlib.import_module(MODULE) # import stable_baselines3
model_attr = getattr(module, MODEL) # e.g. from stable_baselines3 import A2C

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

def create_directories():
    # create the necessary directories
    models_dir = os.path.join(script_dir, f"models/{NAMESPACE}/{MODEL}")
    tf_logs_dir = os.path.join(script_dir, f"tf_logs/{NAMESPACE}/{MODEL}")
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
def setup_environment(alpha, 
                      cluster, 
                      url, 
                      name, 
                      namespace, 
                      minReplicas, 
                      maxReplicas,
                      rew_fun):

    # Construct the absolute file path for queries.json
    queries_json_path = os.path.join(script_dir, "queries.json")

    q_file = open(queries_json_path, "r")
    data = json.load(q_file)
    # QUERIES FOR FRONTEND DEPLOYMENT
    _queries = data[cluster][namespace]
    queries = [
        _queries["q_pod_replicas"],
        _queries["q_request_duration"],
        _queries["q_cpu_usage"],
        _queries["q_memory_usage"],
    ]
    q_file.close()

    # Create an instance of GymEnvironment
    env = GymEnvironment(alpha, 
                         queries, 
                         url, 
                         name, 
                         namespace, 
                         minReplicas, 
                         maxReplicas, 
                         rew_fun)
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
        model = model_attr("MlpPolicy", env, learning_rate=0.01, verbose=1, tensorboard_log=tf_logs_dir)

    return model

def train_model(model, models_dir):
    TIMESTEPS = 100
    # training
    for i in range(1,10):
        print("Learning. Iteration: ", TIMESTEPS*i)
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=MODEL, log_interval=2)
        # model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False)
        logging.info(f"Training iteration {i}, total_timesteps={TIMESTEPS*i}, saving model ...")
        print("Saving model ...")
        model.save(f"{models_dir}/{TIMESTEPS*i}")

    print("Training completed. Check performance on Tensorboard.")
    logging.info("Training completed. Check performance on Tensorboard.")

    return

if __name__ == "__main__":

    # cluster = "minikube"
    cluster = CLUSTER
    url = 'http://prometheus.istio-system.svc.cluster.local:9090'  # URL for Prometheus API
    name = "frontend" # deployment name
    #  namespace = "rl-agent" # namespace
    namespace = NAMESPACE
    minReplicas = 1
    maxReplicas = 30
    rew_fun = REWARD_FUNCTION
    # define alpha based on the selected reward function
    if rew_fun == "indicator": alpha = 100
    elif rew_fun == "quadratic": alpha = 2
    else: print("Could not set alpha.")

    dirs = create_directories()
    models_dir = dirs[0]
    tf_logs_dir = dirs[1]
    pod_logs_dir = dirs[2]
    logger = enable_logging(pod_logs_dir)
    env = setup_environment(alpha, 
                            cluster, 
                            url, 
                            name, 
                            namespace, 
                            minReplicas, 
                            maxReplicas, 
                            rew_fun)
    env = Monitor(env, tf_logs_dir)
    model = load_model(env, models_dir, tf_logs_dir)
    train_model(model, models_dir)

    env.close()