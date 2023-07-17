import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import os

def get_mean_Gt(folder: str) -> tuple[float, float, dict]:
    """
    Compute mean and std of total rewards for best episodes.
    """
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join(script_dir, folder)
    # Check for existing files in state space folder
    existing_files = [f for f in os.listdir(dir)]
    print(f"Existing files: {existing_files}")
    Gt = []
    abs_best = {'episode': 0, 'Gt': -np.Inf}
    if existing_files:
        # Save content of each CSV file in a dataframe
        for file in existing_files:
            df = pd.read_csv(f"{dir}/{file}", encoding='utf-8')
            # print(f"df: {df}")
            rew = df['Value'].tail(1).iloc[0]
            # Get total reward at the end of the episode
            Gt.append(rew)
            # Get best episode
            if rew >= max(Gt):
                abs_best.update({'episode': file, 'Gt': rew})
                # abs_best['Gt'] = rew
            # print(f"Total reward end of episode: {Gt}")
    else:
        print("Error - No files.")
        return None
    mean_Gt = round(np.mean(Gt),2)
    std_Gt = round(np.std(Gt),2)
    return mean_Gt, std_Gt, abs_best

mean_Gt, std_Gt, abs_best = get_mean_Gt('timeseries/tensorboard/S1')
print(f"mean Gt: {mean_Gt}, std: {std_Gt}")
best_ep = [32, 37, 73, 115, 149]
mean_ep = round(np.mean(best_ep),2)
std_ep = round(np.std(best_ep),2)
print(f"mean Gt: {mean_ep}, std: {std_ep}, abs_best: {abs_best}")

