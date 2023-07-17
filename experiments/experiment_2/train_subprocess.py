import subprocess as sub
import os

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
models_path = os.path.join(script_dir, "/models/rl-agent-2/A2C/")
print(f"models_path: {models_path}")
# models_dirs = [folder for folder in os.listdir(models_path)].sort()
print(f"Sorted models_dirs")

S2=["CPU", "p95", "mem"]
S3=["CPU", "p95"]
S4=["p95", "mem"]
S5=["rps", "p95"]
S6=["p95"]

states = [S2, S3, S4, S5, S6]

for state in states:
    print(f"State {state}")
    # Perform 5 runs for each state
    for i in range(0,5):
        c_agent_learn = ["echo",
            "python3", "agent_learn.py",
            "--deployment", "productcatalogservice",
            "--namespace", "rl-agent-2",
            "--cluster", "local",
            "--model", "A2C",
            "--rew_fun", "linear_1",
            "--learn_rate", "0.0007",
            "--metrics",
        ]
        c_agent_learn.extend(state)  # Append the elements of state to the command list
        sub.run(c_agent_learn)
        # After the run, pick best episode and delete log files
        c_runs = ["echo", "Run number "]
        c_runs.extend(f"{i}")
        sub.run(c_runs)
        # Pick best episode:
        # Take last model in last folder 2023_07_...
        existing_models = [f for f in os.listdir(models_dir)]
        # if existing_models:
        #     # Sort models by their names to get the last saved model
        #     existing_models.sort()
        #     last_saved_model = existing_models[-1]

