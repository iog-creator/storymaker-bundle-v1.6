#!/usr/bin/env python3
"""
Setup script for pmagent package
"""

from setuptools import setup, find_packages

setup(
    name="pmagent",
    version="0.0.0",
    description="Project Management Agent CLI",
    author="AgentPM Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "typer>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "pmagent=pmagent.cli:main",
        ],
    },
)
