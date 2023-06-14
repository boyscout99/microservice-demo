# For experiment 2.2, I need something that updates replicas 
# on all namespaces from within the cluster.
import time
from datetime import datetime, timedelta
import logging
import os
import sys
from Scale import KubernetesEnvironment
from Logger import LoggerWriter

NAMESPACE = "rl-agent-e5-a2c"
MODEL = "A2C"

t = datetime.now()
t = t + timedelta(hours=2) # UTC+2
timestamp = t.strftime("%Y_%m_%d_%H%M%S")
# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
pod_logs_dir = os.path.join(script_dir, f"pod_logs/{NAMESPACE}/{MODEL}")

def enable_logging(pod_logs_dir):
    pod_log_file = os.path.join(pod_logs_dir, f"{MODEL}_learn_{timestamp}.log")
    # logging.basicConfig(filename=pod_log_file, level=logging.DEBUG)  # Initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format=f"{timestamp} [%(levelname)s] %(message)s",
        filename=pod_log_file
    )
    
    # Define a logger
    my_logger = logging.getLogger(__name__)

    # Redirect console output to logger
    sys.stdout = LoggerWriter(my_logger.info)
    sys.stderr = LoggerWriter(my_logger.error)

    return my_logger

logger = enable_logging(pod_logs_dir)

deployment="productcatalogservice"
namespaces=[
    "default",
    "testing",
    "rl-agent-e1-a2c",
    "rl-agent-e1-ppo",
    "rl-agent-e3-1",
    "rl-agent-e3-2",
    "rl-agent-e4-1",
    "rl-agent-e5-a2c"
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