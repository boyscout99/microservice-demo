import os

from stable_baselines3 import A2C
# from stable_baselines3.common.monitor import Monitor

from agent_env import GymEnvironment

models_dir = "models/A2C_agent"
logs_dir = "logs/A2C_agent"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Define the hyperparameters for training
alpha = 100  # Your desired value for alpha
# QUERIES FOR FRONTEND DEPLOYMENT
# request duration [ms]
q_request_duration = 'rate(istio_request_duration_milliseconds_count{app="frontend", response_code="200",response_flags="-",request_protocol="http",source_app="loadgenerator"}[1m])'
# cpu utilisation [%]
q_cpu_usage = 'rate(container_cpu_usage_seconds_total{pod=~"frontend-.*"}[1m])/0.2'
# memory usage [Mb]
# !TODO change the image name
q_memory_usage = 'rate(container_memory_usage_bytes{pod=~"frontend-.*"}[1m])/1000000'
# number of replicas per deployment
q_pod_replicas = 'count(kube_pod_info{pod=~"frontend-.*"})'

# list of queries
queries = [
    q_pod_replicas,
    q_request_duration,
    q_cpu_usage,
    q_memory_usage
]

url = 'http://prometheus.istio-system.svc.cluster.local:9090'  # URL for Prometheus API
name = "frontend" # deployment name
namespace = "rl-agent" # namespace

# Create an instance of GymEnvironment
env = GymEnvironment(alpha, queries, url, name, namespace)
# set default state
env.reset()
# Wrap the environment with Monitor to log training stats
# env = Monitor(env, logs_dir)
# Create the A2C model
model = A2C("MlpPolicy", env, verbose=1, tensorboard_log=logs_dir)

TIMESTEPS = 10000
# training
for i in range(1,100000):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="A2C")
    model.save(f"{models_dir}/{TIMESTEPS*i}")

env.close()