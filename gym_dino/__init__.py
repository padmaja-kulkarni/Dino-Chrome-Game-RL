from gym.envs.registration import register

register(
    id='Dino-v0',
    entry_point='gym_dino.dino_env:DinoEnv',
    max_episode_steps=500,
)
