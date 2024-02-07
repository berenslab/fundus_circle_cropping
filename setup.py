#!/usr/bin/python3

import setuptools
from fundus_circle_cropping import about

with open("README.md", "r", encoding='utf8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name=about.__title__,
    version=about.__version__,
    author=about.__author__,
    author_email=about.__email__,
    description=about.__summary__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about.__url__,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    python_requires='>=3.6, <3.12',  # ray is not working with python python >3.11 (https://github.com/ray-project/ray/issues/40211)
)