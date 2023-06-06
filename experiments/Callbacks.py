from stable_baselines3.common.callbacks import BaseCallback
import numpy as np
import os

class TensorboardCallback(BaseCallback):
    def __init__(self, verbose=1):
        super(TensorboardCallback, self).__init__(verbose)
        self.episode_rewards = []
        self.ep_rew_mean = 0
        self.replicas = 0
        self.t = 0
        self.cpu = 0
        self.mem = 0
        self.rps = 0

    def _on_rollout_start(self) -> None:
        self.episode_rewards = []
        self.replicas = 0
        self.t = 0
        self.cpu = 0
        self.mem = 0
        self.rps = 0


    def _on_step(self) -> bool:
        rewards = self.training_env.get_attr("reward")
        self.episode_rewards.extend(rewards)
        obs = self.training_env.get_attr("current_observation")
        self.replicas = obs[0][0]
        self.t = obs[0][1]
        self.rps = obs[0][2]
        self.cpu = obs[0][3]
        self.mem = obs[0][4]
        self.logger.record("rollout/replicas", self.replicas)
        self.logger.record("rollout/t", self.t)
        self.logger.record("rollout/rps", self.rps)
        self.logger.record("rollout/cpu", self.cpu)
        self.logger.record("rollout/mem", self.mem)
        return True

    def _on_rollout_end(self) -> None:
        self.ep_rew_mean = np.mean(self.episode_rewards)
        self.logger.record("rollout/ep_rew_mean", self.ep_rew_mean)
        self.episode_rewards = []
        print("self.ep_rew_mean: ", self.ep_rew_mean)

class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).

    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), 'timesteps')
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-100:])
              if self.verbose > 0:
                print("Num timesteps: {}".format(self.num_timesteps))
                print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(self.best_mean_reward, mean_reward))

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose > 0:
                    print("Saving new best model to {}".format(self.save_path))
                  self.model.save(self.save_path)

        return True
