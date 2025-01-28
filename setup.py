from setuptools import setup, find_packages

setup(
    name="vlsm-calculator",
    version="0.1",
    description="A VLSM calculator that calculates subnet masks and IP ranges for given hosts and generates subnet tables.",
    author="GutsNet",
    license="MIT License",
    url="https://github.com/GutsNet/VLSM", 
    packages=find_packages(),
    install_requires=[
        "tabulate",  # Add other dependencies if needed
        "termcolor",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'vlsm = vlsm.vlsm:main',  
        ],
    },
)
