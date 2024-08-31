import gym
from gym import spaces
import numpy as np
import time
from selenium import webdriver
from PIL import Image, ImageOps
import io



class DinoEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(DinoEnv, self).__init__()

        self.game_url = "file:///Users/padmajakulkarni/PycharmProjects/Dino-Chrome-Game-RL/Dinosaur-Chrome-Game-master/index.html"

        # Define action and observation space
        # Assume action space is binary: 0 -> do nothing, 1 -> jump (spacebar)
        self.action_space = spaces.Discrete(2)

        # Observation space: The size of the screenshot (in grayscale)
        self.observation_space = spaces.Box(low=0, high=255, shape=(200, 300), dtype=np.uint8)

        self.reset()



    def reset(self):
        # Reset the game state
        # Selenium setup
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
        self.driver = webdriver.Firefox()
        self.driver.get(self.game_url)

        # Wait for the game to load
        time.sleep(0.1)
        while True:
            try:
                game_exists = self.driver.execute_script("return typeof Game !== 'undefined';")
                if game_exists:
                    break
            except Exception as e:
                print("Waiting for Game to be defined...")

            time.sleep(0.01)

        self.crashed = False

        self._press_spacebar()  # Simulate spacebar press to start/restart the game

        return self._get_observation()

    def step(self, action):
        # Perform the action in the game
        if action == 1:
            self._press_spacebar()

        # Check if the game is over
        self.crashed = self.driver.execute_script("return window.is_finished;")
        score = self.driver.execute_script("return window.currentScore;")

        # Construct observation, reward, done, info
        observation = self._get_observation()
        reward = score  # You may choose a different reward mechanism
        done = self.crashed
        info = {"score": score, "done": done}

        if done:
            self.driver.quit()

        #print("Reward", reward, ",   Done", done)

        return observation, reward, done, info

    def render(self, mode='human'):
        # Rendering is handled by the browser
        pass

    def close(self):
        self.driver.quit()

    def _start_game(self):
        self._press_spacebar()

    def _press_spacebar(self):
        # Simulate a spacebar press to start or reset the game
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


    def _get_observation(self):
        # Take a screenshot of the game window and load the image directly in memory
        screenshot = self.driver.get_screenshot_as_png()  # Capture the screenshot directly in memory
        image = Image.open(io.BytesIO(screenshot))  # Load the image from memory

        # Crop the image and resize it in one go (Pillow allows resizing after cropping)
        right = image.width
        bottom = int(image.height * 0.5)
        image = image.crop((0, 0, right, bottom)).resize((300, 200), Image.Resampling.LANCZOS)

        # Convert the image to grayscale directly
        image = ImageOps.grayscale(image)

        #image.save('screenshot.png')

        # Convert the image to a 2D numpy array in one step
        observation = np.asarray(image, dtype=np.uint8)

        return observation  # 2D array with shape (200, 300)

        return observation  # 2D array with shape (200, 300)


# Usage example
if __name__ == "__main__":
    game_url = "file:///Users/padmajakulkarni/PycharmProjects/Dino-Chrome-Game-RL/Dinosaur-Chrome-Game-master/index.html"
    env = DinoEnv(game_url)

    observation = env.reset()
    done = False

    while not done:
        action = env.action_space.sample()  # take a random action
        observation, reward, done, info = env.step(action)
        #print(f"Reward: {reward}, Done: {done}, Info: {info}")

        if done:
            observation = env.reset()  # Reset the game when done

    env.close()
