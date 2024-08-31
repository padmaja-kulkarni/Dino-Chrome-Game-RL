import os
import pickle
import gym
import gym_dino
from stable_baselines3 import PPO
from gym_dino.dino_env import DinoEnv
from stable_baselines3.common.callbacks import BaseCallback

os.environ['MOZ_HEADLESS'] = '0'

# Define paths
model_path = "../models/dino_model.zip"
metadata_path = "../models/metadata.pkl"
timesteps_to_learn = 3000

# Load metadata if it exists
if os.path.exists(metadata_path):
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    initial_episode_count = metadata.get('episode_count', 0)
    cumulative_timesteps = metadata.get('total_timesteps', 0)
else:
    initial_episode_count = 0
    cumulative_timesteps = 0


class EpisodeCounterCallback(BaseCallback):
    def __init__(self, initial_episode_count=0, verbose=0):
        super(EpisodeCounterCallback, self).__init__(verbose)
        self.episode_count = initial_episode_count

    def _on_step(self) -> bool:
        if self.locals["dones"][0]:  # Check if the first environment is done
            self.episode_count += 1
            if self.episode_count % 10 == 0:
                print(f"Total episodes completed: {self.episode_count}")
        return True

    def _on_training_end(self) -> None:
        print(f"Total episodes completed: {self.episode_count}")

# Initialize the callback with the loaded episode count
callback = EpisodeCounterCallback(initial_episode_count=initial_episode_count)

# Check if the model exists
if os.path.exists(model_path):
    print("Model found. Loading the model...")
    model = PPO.load(model_path)
    # Re-initialize the environment
    env = DinoEnv()  # Replace with your environment
    model.set_env(env)
else:
    print("Model not found. Initializing a new model...")
    env = DinoEnv()  # Replace with your environment
    model = PPO('MlpPolicy', env, verbose=1)

# Continue training the model
model.learn(total_timesteps=timesteps_to_learn, callback=callback)

# Update cumulative timesteps
cumulative_timesteps += timesteps_to_learn  # Add the current session's timesteps


# Save the trained model
model.save("../models/dino_model")

# Save updated metadata
metadata = {
    'episode_count': callback.episode_count,
    'total_timesteps': cumulative_timesteps,  # This includes previous timesteps
    'learning_rate': model.learning_rate,
    # Add other relevant metrics or hyperparameters
}

with open(metadata_path, 'wb') as f:
    pickle.dump(metadata, f)

# Print cumulative stats
print(f"Cumulative Timesteps: {cumulative_timesteps}")
print(f"Cumulative Episodes: {callback.episode_count}")