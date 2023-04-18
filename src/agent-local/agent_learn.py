import os

from stable_baselines3 import A2C
# from stable_baselines3.common.monitor import Monitor

from agent_env import GymEnvironment

models_dir = "models/"
logs_dir = "logs/"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Define the hyperparameters for training
alpha = 100  # Your desired value for alpha
# QUERIES FOR FRONTEND DEPLOYMENT
# take slowest service request duration [ms]
# request duration [ms]
q_request_duration = 'max(rate(istio_request_duration_milliseconds_count{pod=~"frontend-.*", request_protocol="grpc", response_code="200", namespace="rl-agent"}[1m]))'
# cpu utilisation [%]
q_cpu_usage = 'rate(container_cpu_usage_seconds_total{pod=~"frontend-.*", namespace="rl-agent"}[1m])/0.1*100'
# memory usage [%]
q_memory_usage = 'rate(container_memory_usage_bytes{pod=~"frontend-.*", namespace="rl-agent"}[1m])/64000000'
# number of replicas per deployment
q_pod_replicas = 'count(kube_pod_info{pod=~"frontend-.*", namespace="rl-agent"})'

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
minReplicas = 1
maxReplicas = 10

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