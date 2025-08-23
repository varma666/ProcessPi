from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="processpi",  # Make sure this matches your PyPI package name
    version="0.1.1",
    author="Raviteja Varma Nadimpalli",
    author_email="your_email@example.com",  # replace with your email
    description="Python toolkit for chemical engineering simulations, equipment design, and unit conversions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varma666/ProcessPi",  # replace with your repo URL
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.8",
    install_requires=[
        # Add your package dependencies here, e.g.:
        # "numpy>=1.25",
        # "scipy>=1.11",
        # "pandas>=2.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # adjust license if needed
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/varma666/ProcessPi/issues",
        "Documentation": "https://github.com/varma666/ProcessPi#readme",
        "Source Code": "https://github.com/varma666/ProcessPi",
    },
)
