import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import os

def get_mean_Gt(folder: str) -> tuple[float, float]:
    """
    Compute mean and std of total rewards for best episodes.
    """
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join(script_dir, folder)
    # Check for existing files in state space folder
    existing_files = [f for f in os.listdir(dir)]
    Gt = []
    if existing_files:
        # Save content of each CSV file in a dataframe
        for file in existing_files:
            df = pd.read_csv(f"{dir}/{file}")
            # Get total reward at the end of the episode
            Gt.append(df['Value'].tail(1).iloc[0])
            # print(f"Total reward end of episode: {Gt}")
    else:
        print("Error - No files.")
        return None
    mean_Gt = round(np.mean(Gt),2)
    std_Gt = round(np.std(Gt),2)
    return mean_Gt, std_Gt

# Read data from DataFrame
# Total reward Gt
df_tot_rew = pd.read_csv('timeseries/tensorboard/S1_rew_1.csv')
# Replicas
df_rep = pd.read_csv('timeseries/tensorboard/S1_rep_1.csv')
# Latency
df_p95 = pd.read_csv('timeseries/tensorboard/S1_p95_1.csv')

# Fill missing values with 0
df_tot_rew.fillna(0, inplace=True)
df_rep.fillna(0, inplace=True)
df_p95.fillna(0, inplace=True)

timesteps = df_tot_rew['Step']
tot_rew = df_tot_rew['Value']
# Get total reward at the end of the episode
Gt = df_tot_rew['Value'].tail(1).iloc[0]
print(f"Total reward end of episode: {Gt}")

# Get the mean replicas used
rep = df_rep['Value']
mean_rep = np.mean(rep)
std_rep = np.std(rep)
print(f"Mean replicas: {mean_rep}, std {std_rep}")

# Get SLA violations
p95 = df_p95['Value']
violations = df_p95[df_p95['Value']>5]['Value'].count()/df_p95['Value'].count()
print(f"Violations {violations}")

mean_Gt, std_Gt = get_mean_Gt('timeseries/tensorboard/S1')
print(f"mean Gt: {mean_Gt}, std: {std_Gt}")
