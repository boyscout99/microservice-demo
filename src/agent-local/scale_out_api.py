from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Load the Kubernetes configuration
config.load_kube_config()
# Create in instance of the K8s API client
api = client.AppsV1Api()
# Simulate and action of the RL agent
actions_space = [-1, 0, 1] # scale in, do not scale, scale out
action = actions_space[2]
# Get current number of replicas of the Deployment
name = "frontend"
namespace = "rl-agent"
try:
    deployment = api.read_namespaced_deployment_scale(
        name = name,
        namespace = namespace
    )
    if deployment.spec.replicas is not None:
        current_replicas = int(deployment.spec.replicas)
    else:
        current_replicas = 0

    print("Current replicas: ", current_replicas)

except ApiException as e:
    print("Exception when calling AppsV1Api->read_namespaced_deployment_scale: %s\n" % e)

# Update the number of replicas
deployment.spec.replicas = current_replicas + action
try:
    api.replace_namespaced_deployment_scale(
        name = name,
        namespace = namespace,
        body = deployment
    )
    print("New number of replicas: ", deployment.spec.replicas)
except ApiException as e:
    print("Exception when calling AppsV1Api->replace_namespaced_deployment_scale: %s\n" % e)