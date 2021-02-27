from setuptools import setup, find_packages

with open("README.md") as f:
    LONG_DESC = f.read()

setup(
    name="vicsek",
    version=2.0,
    description="Implementation of the Vicsek model of active matter",
    author="Joe Marsh Rossney",
    url="https://github.com/marshrossney/vicsek",
    long_description=LONG_DESC,
    package=find_packages(),
    entry_points={
        "console_scripts": [
            "vic-anim = vicsek.scripts.shell_scripts:anim",
            "vic-time = vicsek.scripts.shell_scripts:time",
            "vic-evol = vicsek.scripts.shell_scripts:evol",
        ]
    },
)
