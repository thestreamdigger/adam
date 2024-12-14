from setuptools import setup, find_packages

setup(
    name="adam",
    version="2.0.0",
    packages=find_packages(),
    package_dir={"": "."},
    python_requires=">=3.7",
    install_requires=[
        "python-mpd2>=3.1.1",
        "gpiozero>=2.0.1",
        "watchdog>=6.0.0",
        "lgpio>=0.2.2.0",
        "psutil>=5.8.0",
    ],
    author="StreamDigger",
    description="Adam for MPD",
    package_data={
        'adam': ['config/*.json'],
    },
    include_package_data=True,
)
