#!/usr/bin/env python

import pathlib
import pkg_resources

from setuptools import find_packages, setup
from signalfx_azure_function_python.version import name, version

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(
    name=name,
    version=version,
    packages=find_packages(include=["signalfx_azure_function_python"]),
    description="SignalFx Azure Function Python Wrapper",
    author="Jérémy Marmol",
    author_email="jeremy.marmol@fr.clara.net",
    install_requires=install_requires,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    url="https://github.com/claranet/signalfx-azure-function-python",
)
