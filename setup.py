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
        "lgpio>=0.2.2.0",
        "psutil>=5.8.0",
    ],
    author="Streamdigger",
    description="Minimalist moOde interface on Raspberry Pi with a TM1637 display delivering cool digital-retro flair",
    license="GNU General Public License v3.0",
    package_data={
        'adam': ['config/*.json'],
    },
    include_package_data=True,
)
