from setuptools import setup, find_packages

setup(
    name='DinoChromeGameRL',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'gym',
        'stable-baselines3',
        'selenium',
        'Pillow',
        'webdriver-manager',
        # Add other dependencies as needed
    ],
    include_package_data=True,
    package_data={
        '': ['*.html'],  # Include any HTML files
    },
    entry_points={
        'console_scripts': [
            # Add console scripts if needed
        ],
    },
)
