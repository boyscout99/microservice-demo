import os

import gym
from stable_baselines3 import PPO

models_dir = "models/PPO2"
logs_dir = "logs/PPO2"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Create the environment
env = gym.make('LunarLander-v2')  # continuous: LunarLanderContinuous-v2
# required before you can step the environment
env.reset()
# take a model
model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=logs_dir)

TIMESTEPS = 10
# training
for i in range(1,30):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO")
    model.save(f"{models_dir}/{TIMESTEPS*i}")

env.close()