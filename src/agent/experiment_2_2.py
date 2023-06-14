from Scale import KubernetesEnvironment
import time

deployment="productcatalogservice"
namespaces=[
    "default",
    "testing",
    "rl-agent-e1-a2c",
    "rl-agent-e1-ppo",
    "rl-agent-e3-1",
    "rl-agent-e3-2",
    "rl-agent-e4-1"
]
replicas=1
while replicas <=15:
    for namespace in namespaces:
        print(f"Scaling deployment {deployment} in namespace {namespace} to {replicas} replicas.")
        scale = KubernetesEnvironment(deployment, namespace, 1, 15)
        scale.update_replicas(+1)

    print("Waiting 660 seconds ...") 
    time.sleep(660)  # Wait for loadgen experiment to finish
    replicas +=1