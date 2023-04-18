from stable_baselines3.common.env_checker import check_env
from agent_env import GymEnvironment

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
minReplicas = 1
maxReplicas = 10

# Create an instance of GymEnvironment
env = GymEnvironment(alpha, queries, url, name, namespace)


# It will check your custom environment and output additional warning if needed
check_env(env)
