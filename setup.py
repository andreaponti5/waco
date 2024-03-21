from codecs import open
from os import path

from setuptools import setup

ROOT = path.abspath(path.dirname(__file__))

with open(path.join(ROOT, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="waco",
    version="0.1.0",
    description="Simulate the diffusion of contaminants in water networks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Andrea Ponti",
    author_email="ponti.andrea97@gmail.com",
    license="MIT",
    url="https://andreaponti5.github.io/waco",
    project_urls={
        "Documentation": "https://andreaponti5.github.io/waco",
        "Source": "https://github.com/andreaponti5/waco",
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent"
    ],
    packages=["waco"],
    include_package_data=True,
    install_requires=["wntr"]
)
