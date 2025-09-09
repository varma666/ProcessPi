__version__ = "0.1.2.12"

from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="processpi",
    version=__version__,
    author="Raviteja Varma Nadimpalli",
    author_email="processpi.dev@gmail.com",
    description="Python toolkit for chemical engineering simulations, equipment design, and unit conversions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varma666/ProcessPi",
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.8",
    install_requires=[
        "tabulate>=0.9.0",
        "matplotlib>=3.7.0",
        "networkx>=3.1",
        "CoolProp>=6.5.0",
        "tqdm>=4.65.0",
        "plotly>=5.18.0",  # Added Plotly for interactive visualizations
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemical Engineering",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/varma666/ProcessPi/issues",
        "Documentation": "https://github.com/varma666/ProcessPi#readme",
        "Source Code": "https://github.com/varma666/ProcessPi",
    },
    entry_points={
        "console_scripts": [
            "processpi=processpi.cli:main",  # CLI entry point
        ],
    },
)
