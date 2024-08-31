import gym
import gym_dino
from stable_baselines3 import PPO

env = gym.make('Dino-v0')
model = PPO.load("../models/dino_model")

obs = env.reset()
done = False

while not done:
    action, _ = model.predict(obs)
    obs, reward, done, info = env.step(action)
    env.render()
