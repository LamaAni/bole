import os
import re
from setuptools import setup, find_packages
import logging

REPO_PATH = os.path.dirname(os.path.abspath(__file__))
VERSION_PATH = os.path.abspath(os.environ.get("VERSION_PATH", os.path.join(REPO_PATH, ".version")))
GITHUB_URL = "https://github.com/LamaAni/bole"

packages = find_packages()


# Get the long description from the README file
with open(os.path.join(REPO_PATH, "README.md"), "r") as readme:
    long_description = readme.read()

with open(os.path.join(REPO_PATH, "requirements.txt"), "r") as requirements_file:
    requirements_text = requirements_file.read()
    requirements_text = re.sub(r"[#].*", "", requirements_text)
    requirement_list = [r.strip() for r in requirements_text.split("\n") if len(r.strip()) > 0]

version = None
if os.path.isfile(VERSION_PATH):
    with open(VERSION_PATH, "r") as file:
        version = file.read()
else:
    logging.info("Version file not found @ " + VERSION_PATH)
    logging.info("Using default version debug")

version = version or os.environ.get("SETUP_VERSION", "debug")

setup(
    name="bole",  # Required
    version=version,  # Required
    description="Easy logger and cascading configuration manager for python (yaml, json)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=GITHUB_URL,
    author="Zav Shotan",
    keywords="configuration config log yaml json",
    packages=packages,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "bole=bole.__main__:run_cli_main",
        ],
    },
    install_requires=requirement_list,
    project_urls={
        "Source": GITHUB_URL,
    },
)
