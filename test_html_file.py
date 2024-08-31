import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

# Explicitly set the MOZ_HEADLESS environment variable
#os.environ['MOZ_HEADLESS'] = '0'  # Force headless mode

# Path to the local Dino game HTML file
file_url = "file:///Users/padmajakulkarni/PycharmProjects/Dino-Chrome-Game-RL/Dinosaur-Chrome-Game-master/index.html"

driver = webdriver.Firefox()

try:
    # Open the locally saved Dino game
    driver.get(file_url)

    # Wait for the page to load completely
    time.sleep(0.1)

    # Wait for the Game object to be available
    while True:
        try:
            game_exists = driver.execute_script("return typeof Game !== 'undefined';")
            if game_exists:
                break
        except Exception as e:
            print("Waiting for Game to be defined...")

        time.sleep(0.01)

    # Start the game by simulating a spacebar press
    driver.execute_script("""
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
    driver.execute_script("""
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

    # Keep the game running and check if the game is crashed
    crashed = False

    while not crashed:
        try:
            # Check if the game is finished (crashed)
            crashed = driver.execute_script("return window.is_finished;")

            if crashed:
                print("Game Over!", crashed)
            else:
                print("Game is running...", crashed)

            # Retrieve the current score
            score = driver.execute_script("return window.currentScore;")
            print("Current Score:", score)

        except Exception as e:
            print("Error retrieving game status:", e)

        time.sleep(0.05)  # Adjust the sleep time to control the checking interval

finally:
    # Close the browser
    driver.quit()
