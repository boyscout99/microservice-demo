import subprocess as sub
import shutil 
from shlex import quote
import os

# Get the absolute path of the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# print(f"script_dir: {script_dir}")
models_path = os.path.join(script_dir, 'models/rl-agent-2/A2C/')
tf_logs_path = os.path.join(script_dir, 'tf_logs/rl-agent-2/A2C/')
# print(f"models_path: {models_path}, tf_logs_path: {tf_logs_path}")
folders = sorted(os.listdir(models_path))
# print(f"folders: {folders}")

S2=['CPU', 'p95', 'mem']
S3=["CPU", "p95"]
S4=["p95", "mem"]
S5=["rps", "p95"]
S6=["p95"]

states = [S2, S3, S4, S5, S6]
# states = [S2]

for state in states:
    print(f"State {state}")
    # Perform 5 runs for each state
    for i in range(0,5):
        print(f"Run number {i}")
        # print(f"{type(' '.join([quote(metric) for metric in state]))}")\
        result = ' '.join(f'{s}' for s in state)
        print(result)
        c_agent_learn = [
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
        # Pick best episode:
        # Take last model in last folder 2023_07_...
        folders = sorted(os.listdir(models_path))
        last_model_folder = os.path.join(models_path, folders[-1])
        # print(f"Last model folder: {last_model_folder}")
        existing_models = [f for f in os.listdir(last_model_folder)]
        # print(f"existing_models: {existing_models}")
        try:
            # Sort models by their names to get the last saved model
            existing_models.sort(key=lambda  x: int(x.split('.')[0]))
            last_saved_model = existing_models[-1]
            best_model_number = last_saved_model.split('.')[0]
            print(f"last_saved_model: {last_saved_model}, number: {best_model_number}")
        except Exception as e:
            print(f"ERROR in picking best model - {e}")
        # Delete all other models
        for model in existing_models:
            file_path = last_model_folder + '/' + model
            if file_path != last_model_folder + '/' + last_saved_model:
                # print(f"Remove: {file_path}")
                os.remove(file_path)

        # Delete all tf_logs/ except best
        folders = sorted(os.listdir(tf_logs_path))
        last_tf_folder = os.path.join(tf_logs_path, folders[-1])
        # print(f"Last tf folder: {last_tf_folder}")

        best_tf_log = "A2C_" + best_model_number
        for log in os.listdir(last_tf_folder):
            file_path = last_tf_folder + '/' + log
            if file_path != last_tf_folder + '/' + best_tf_log:
                # print(f"Remove: {file_path}")
                shutil.rmtree(file_path)
                # os.rmdir(file_path)


