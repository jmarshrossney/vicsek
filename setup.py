from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESC = f.read()

setup(
    name="vicsek",
    version=0.3,
    description="Implementation of the Vicsek model of active matter",
    author="Joe Marsh Rossney",
    url="https://github.com/marshrossney/vicsek",
    long_description=LONG_DESC,
    package=find_packages(),
    entry_points={
        "console_scripts": [
            "vic-ani = vicsek.scripts.vic_ani:main",
            "vic-snap = vicsek.scripts.vic_snap:main",
            "vic-ens = vicsek.scripts.vic_ens:main",
        ]
    },
)
