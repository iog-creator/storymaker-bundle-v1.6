from setuptools import setup, find_packages

setup(
    name="pmagent",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        "jsonschema>=4.25.0",
        "typer>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "pmagent=pmagent.cli:main",
        ],
    },
)
