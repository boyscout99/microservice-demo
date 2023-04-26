import os
import json
import logging
from stable_baselines3 import A2C
# from stable_baselines3.common.monitor import Monitor
from agent_env import GymEnvironment
from datetime import datetime

MODEL = "A2C"
print(f"Using model {MODEL}.")

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
logging.basicConfig(filename=f"{MODEL}_learn_{timestamp}.log", level=logging.DEBUG)  # Initialize logging

models_dir = f"models/{MODEL}"
logs_dir = f"logs/{MODEL}"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute file path for queries.json
queries_json_path = os.path.join(script_dir, "queries.json")

q_file = open("queries.json", "r")
data = json.load(q_file)

# Define the hyperparameters for training
alpha = 100  # Your desired value for alpha
# QUERIES FOR FRONTEND DEPLOYMENT
_queries = data["gke"]
queries = [
    _queries["q_pod_replicas"],
    _queries["q_request_duration"],
    _queries["q_cpu_usage"],
    _queries["q_memory_usage"],
]
q_file.close()

url = 'http://prometheus.istio-system.svc.cluster.local:9090'  # URL for Prometheus API
name = "frontend" # deployment name
namespace = "rl-agent" # namespace
minReplicas = 1
maxReplicas = 30

# Create an instance of GymEnvironment
env = GymEnvironment(alpha, queries, url, name, namespace, minReplicas, maxReplicas)
# set default state
env.reset()
# Wrap the environment with Monitor to log training stats
# env = Monitor(env, logs_dir)

# Check for existing models and load the last saved model if available
existing_models = [f for f in os.listdir(models_dir)]
if existing_models:
    # Sort models by their names to get the last saved model
    existing_models.sort()
    last_saved_model = existing_models[-1]
    model_path = os.path.join(models_dir, last_saved_model)
    print(f"Loading last saved model: {model_path}")
    logging.info(f"Loading last saved model: {model_path}")
    model = A2C.load(model_path, env=env, tensorboard_log=logs_dir)
else:
    print("No existing models found. Starting from scratch.")
    logging.info("No existing models found. Starting from scratch.")
    # Create the A2C model
    model = A2C("MlpPolicy", env, verbose=1, tensorboard_log=logs_dir)

TIMESTEPS = 20
# training
for i in range(1,10):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=MODEL)
    logging.info(f"Training iteration {i}, total_timesteps={TIMESTEPS*i}, saving model ...")
    print("Saving model ...")
    model.save(f"{models_dir}/{TIMESTEPS*i}")

print("Training completed. Check performance on Tensorboard.")
logging.info("Training completed. Check performance on Tensorboard.")

env.close()