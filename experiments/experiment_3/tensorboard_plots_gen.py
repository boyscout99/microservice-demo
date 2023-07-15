import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import json
import math

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
