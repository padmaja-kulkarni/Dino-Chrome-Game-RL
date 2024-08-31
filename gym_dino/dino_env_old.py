import gym
from gym import spaces
import numpy as np
from PIL import Image
import time
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

class DinoEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, render_mode=False):
        super(DinoEnv, self).__init__()

        # Define the observation and action space
        self.observation_space = spaces.Box(low=0, high=255,
                                            shape=(100, 100, 1), dtype=np.uint8)  # Grayscale image
        self.action_space = spaces.Discrete(2)  # Actions: 0=Do nothing, 1=Jump (Space bar)
        self.render_mode = render_mode
        self.game_over = False
        self.score = 0

        if self.render_mode:
            firefox_options = Options()
            firefox_options.headless = not render_mode  # Headless if render_mode is False

            # Set up the Firefox WebDriver
            self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)

            self.game_url = "file:///Users/padmajakulkarni/PycharmProjects/Dino-Chrome-Game-RL/Dinosaur-Chrome-Game-master/index.html"
            self.driver.get(self.game_url)
            self.driver.execute_script("document.querySelector('body').click();")  # Start the game

    def reset(self):
        if self.render_mode:
            self.driver.refresh()
            time.sleep(1)  # Allow the game to load and reset

        # Reset the game state variables
        self.game_over = False
        self.score = 0

        # Get the initial observation (first frame of the game)
        obs = self._get_observation()

        return obs  # Return the initial observation

    def step(self, action):
        start_time = time.time()

        if self.render_mode:
            self._take_action(action)
        time.sleep(0.01)

        obs = self._get_observation()
        reward = self._compute_reward()
        done = self._is_done()

        step_time = time.time() - start_time

        return obs, reward, done, {"step_time": step_time}

    def _get_observation(self):
        if self.render_mode:
            # Take a screenshot of the game window
            self.driver.save_screenshot('screenshot.png')
            image = Image.open('screenshot.png')

            # Define the bounding box to crop the game area (example values)
            left = 0
            top = 0
            right = image.width
            bottom = int(image.height * 0.5)

            image = image.crop((left, top, right, bottom))
            image = image.resize((100, 100))  # Resize the cropped image to 100x100

            # Convert the image to grayscale (black and white)
            image = image.convert('L')  # 'L' mode is for grayscale

            return np.array(image)[:, :, np.newaxis]  # Add a channel dimension to maintain consistency
        else:
            # Provide a dummy observation if not rendering
            return np.zeros((100, 100, 1), dtype=np.uint8)

    def _take_action(self, action):
        if self.render_mode and action == 1:
            # Press the space bar to jump
            self.driver.execute_script("""
                var event = new KeyboardEvent('keydown', {
                    key: ' ',
                    code: 'Space',
                    keyCode: 32,
                    which: 32,
                    bubbles: true,
                    cancelable: true
                });
                document.dispatchEvent(event);
            """)
            time.sleep(0.01)
            self.driver.execute_script("""
                var event = new KeyboardEvent('keyup', {
                    key: ' ',
                    code: 'Space',
                    keyCode: 32,
                    which: 32,
                    bubbles: true,
                    cancelable: true
                });
                document.dispatchEvent(event);
            """)

    def _compute_reward(self):
        if self.render_mode:
            try:
                # Retrieve the current score from the global JavaScript variable
                score = self.driver.execute_script("return window.currentScore;")
                if score is not None:
                    reward = float(score) - self.score  # Use the increase in score as the reward
                    self.score = float(score)  # Update the stored score
                else:
                    reward = 0.0  # If score is None, return 0 reward

            except Exception as e:
                print("Error retrieving score:", e)
                reward = 0.0  # Default to 0 if there's an error

            return reward
        else:
            # Placeholder reward for non-rendered mode
            self.score += 1  # Increment score as a simple placeholder
            return 1.0

    def _is_done(self):
        if self.render_mode:
            # Check if the game is over
            game_over_element = self.driver.execute_script("return Runner.instance_.crashed;")
            self.game_over = game_over_element
            return self.game_over
        else:
            # Placeholder done condition for non-rendered mode
            return False

    def render(self, mode='human'):
        if self.render_mode:
            # Rendering is automatically handled by the browser window in Selenium
            pass

    def close(self):
        if self.render_mode:
            self.driver.quit()

    def calculate_observations_per_minute(self):
        total_time = 0
        steps = 100  # Number of steps to simulate

        for _ in range(steps):
            _, _, _, info = self.step(0)
            total_time += info["step_time"]

        obs_per_minute = (steps / total_time) * 60
        return obs_per_minute
