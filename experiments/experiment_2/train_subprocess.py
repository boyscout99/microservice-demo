import subprocess as sub
import os

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"script_dir: {script_dir}")
models_path = os.path.join(script_dir, 'models/rl-agent-2/A2C/')
tf_logs_path = os.path.join(script_dir, 'tf_logs/rl-agent-2/A2C/')
print(f"models_path: {models_path}, tf_logs_path: {tf_logs_path}")
folders = sorted(os.listdir(models_path))
print(f"folders: {folders}")

S2=["CPU", "p95", "mem"]
S3=["CPU", "p95"]
S4=["p95", "mem"]
S5=["rps", "p95"]
S6=["p95"]

# states = [S2, S3, S4, S5, S6]
states = [S2]

for state in states:
    print(f"State {state}")
    # Perform 5 runs for each state
    for i in range(0,2):
        c_agent_learn = ["echo",
            "python3", "agent_learn.py",
            "--deployment", "productcatalogservice",
            "--namespace", "rl-agent-2",
            "--cluster", "local",
            "--model", "A2C",
            "--rew_fun", "linear_1",
            "--learn_rate", "0.0007",
            "--metrics"
        ]
        c_agent_learn.extend(state)  # Append the elements of state to the command list
        sub.run(c_agent_learn)
        # After the run, pick best episode and delete log files
        c_runs = ["echo", "Run number "]
        c_runs.extend(f"{i}")
        sub.run(c_runs)
        # Pick best episode:
        # Take last model in last folder 2023_07_...
        folders = sorted(os.listdir(models_path))
        last_folder = os.path.join(models_path, folders[-1])
        print(f"Last folder: {last_folder}")
        existing_models = [f for f in os.listdir(last_folder)]
        print(f"existing_models: {existing_models}")
        try:
            # Sort models by their names to get the last saved model
            existing_models.sort(key=lambda  x: int(x.split('.')[0]))
            last_saved_model = existing_models[-1]
            best_model_number = last_saved_model.split('.')[0]
            print(f"last_saved_model: {last_saved_model}, number: {best_model_number}")
        except Exception as e:
            print(f"ERROR in picking best model - {e}")
        # Delete all other models
        # Go to models directory and create directory best
        c_mkdir = [
            # "echo", 
            "mkdir", f"{last_folder}/best"
        ]
        # Move best model to best/ and remove all other models
        c_rm_models = [
            # "echo",
            "mv", f"{last_saved_model}", f"{last_folder}/best",
            "rm", "-rf", f"{last_folder}/*.zip"
        ]
        sub.run(c_mkdir)
        sub.run(c_rm_models)
        # Go to directory tf_logs/
        c_cd_last_tf_dir = [
            # "echo",
            "cd", f"{tf_logs_path}"
        ]
        sub.run(c_cd_last_tf_dir)
        # Go to last directory
        sub.run(c_cd_last_dir)
        # Create directory best
        sub.run(c_mkdir)
        # Delete all logs except the best one
        best_tf_log = "A2C_"+best_model_number
        c_rm_tf_logs = [
            # "echo",
            "mv", f"{best_tf_log}", "best",
            "rm", "-rf", "A2C_*"
        ]
        sub.run(c_rm_tf_logs)

