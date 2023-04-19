import os
import json

from stable_baselines3 import A2C
# from stable_baselines3.common.monitor import Monitor

from agent_env import GymEnvironment

models_dir = "models/"
logs_dir = "logs/"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

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
# Create the A2C model
model = A2C("MlpPolicy", env, verbose=1, tensorboard_log=logs_dir)

TIMESTEPS = 10000
# training
for i in range(1,100):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="A2C")
    model.save(f"{models_dir}/{TIMESTEPS*i}")

env.close()