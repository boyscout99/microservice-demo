import subprocess
import os
import json
from ArgParser import StringProcessor

host = "http://frontend:80"
processor = StringProcessor()
WORKLOAD_TYPE = processor.parse_args()
script_dir = os.path.dirname(os.path.abspath(__file__))

def init():
    # Initialise the workload to 50 users
    command = ["locust", "--host="+host, "--headless", "-u", str(50), "-r", str(50), "--run-time", str(20)]
    print("Initialising to 50 users. Wait 20 seconds.")
    subprocess.call(command)
    return print("Initialisation finished.")

def periodic_workload():
    """
    This function creates a periodic workload in a window
    of 25 minutes.
    [0,10] steady increase from 0 to 1500 users
    [10] abrupt decrease to 750 users
    [11, 15] constant 750 users
    [15] abrupt decreast to 150 users
    [16, 20] constant 150 users
    [21] abrupt increase to 1000 users
    """
    file_dir = os.path.join(script_dir, "workloads.json")
    file = open(file_dir, "r")
    data = json.load(file)
    # QUERIES FOR FRONTEND DEPLOYMENT
    actions = data[WORKLOAD_TYPE]
    file.close()

    while(True):
        for action in actions:
            print("Action: ", action)
            users = str(action['users'])
            rate = str(action['rate'])
            wait_time = str(action['wait'])
            command = ["locust", "--host", host, "--headless", "-u", users, "--spawn-rate", rate, "--run-time", wait_time]
            print("Creating %s users at a rate of %s per second.", users, rate)
            # get output of command
            subprocess.call(command)

if __name__ == "__main__":
    init()
    periodic_workload()



