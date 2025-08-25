from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="processpi",  
    version="0.1.1",
    author="Raviteja Varma Nadimpalli",
    author_email="processpi.dev@gmail.com",  
    description="Python toolkit for chemical engineering simulations, equipment design, and unit conversions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/varma666/ProcessPi",  
    packages=find_packages(exclude=["tests*", "docs*"]),
    python_requires=">=3.8",
    install_requires=[
        
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # adjust license if needed
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemical Engineering",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/varma666/ProcessPi/issues",
        "Documentation": "https://github.com/varma666/ProcessPi#readme",
        "Source Code": "https://github.com/varma666/ProcessPi",
    },
)
