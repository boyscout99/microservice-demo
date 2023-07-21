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

def get_means(folder:str):
    """
    Plot mean signal Gt, taka std among signals.
    return mean Gt at the last timestep.
    Input: folder <- directory with CSV for 10 runs
    """
    # Get the absolute path of the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir = os.path.join(script_dir, folder)
    # Check for existing files in state space folder
    existing_files = [f for f in os.listdir(dir)]
    print(f"Existing files: {existing_files}")
    tot_rew_dict = {}
    if existing_files:
        # Save content of each CSV file in a dataframe
        for file in existing_files:
            df = pd.read_csv(f"{dir}/{file}", encoding='utf-8')
            # print(f"df: {df}")
            # get reward column
            rewards = df['Value'].tolist()
            # print(f"rewards: {rewards}")
            tot_rew_dict.update({file: rewards})
            # print(f"tot_rew_dict: {tot_rew_dict}")
        # Create new df
        df_tot_rew = pd.DataFrame(tot_rew_dict)
        df_tot_rew['mean Gt'] = df_tot_rew.mean(axis=1)
        df_tot_rew['std Gt'] = df_tot_rew.std(axis=1)
        print(f"dataframe: {df_tot_rew}")
        print(f"mean_gt_end: {df_tot_rew['mean Gt'].tail(1).iloc[0]}, std: {df_tot_rew['std Gt'].tail(1).iloc[0]}")
    else:
        print("Error - No files.")
        return None
    
    return df_tot_rew['mean Gt'].tolist()

# mean_Gt, std_Gt, abs_best = get_mean_Gt('timeseries/tensorboard/rnd_load/S6')
# print(f"mean Gt: {mean_Gt}, std Gt: {std_Gt}")
# best_ep = [4, 15, 16, 20, 105]
# mean_ep = round(np.mean(best_ep),2)
# std_ep = round(np.std(best_ep),2)
# print(f"mean ep: {mean_ep}, std ep: {std_ep}, abs_best: {abs_best}")
mean_Gt = get_means('timeseries/tensorboard/14days_steps/const_load/S4')
steps = np.arange(0,len(mean_Gt))*((2*20160)/1000)

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "sans-serif",
    "font.sans-serif": "Georgia",
    "font.size": 14,
    "figure.dpi": 250
})

plt.plot(steps, mean_Gt, label='$\mu_{G_{T}}$')
plt.title('Training with ${S}_{4}$, constant workload')
plt.xlabel('steps')
plt.ylabel('$\mu_{G_{T}}$')
plt.grid()
plt.legend(loc='upper right', fontsize='x-small')
plt.savefig('const_train_S4.png')

