import subprocess

host = "http://frontend:80"

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
    [0,5] steady increase from 0 to 1500 users
    [5] abrupt decrease to 10 users
    [6, 10] steady increase to 1000 users
    [11, 15] constant level to 1000 users
    [16, 20] abrupt decrease to 50 users
    [21] abrupt increase to 1500 users
    """
    actions = [
        {
        'users': 1500,
        'rate': 30,
        'wait': 60*5,
        },
        {
        'users': 10,
        'rate': 10,
        'wait': 60
        },
        {
        'users': 1000,
        'rate': 25,
        'wait': 60*9
        },
        {
        'users': 50,
        'rate': 50,
        'wait': 60*5
        },
        {
        'users': 1500,
        'rate': 1500,
        'wait': 60*5,
        }
    ]
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



