#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from setuptools import find_packages, setup

settings = dict()
root_path = os.path.dirname(os.path.realpath(__file__))

with open(f"{root_path}/fastflyer/__info__.py", "r",
          encoding="utf-8") as version:
    setup_info = version.read()
    exec(setup_info)

with open(f"{root_path}/README.md", "r", encoding="utf-8") as file_readme:
    readme = file_readme.read()

with open(f"{root_path}/requirements.txt", "r") as file_requirements:
    requirements = file_requirements.read().splitlines()

settings.update(name=__package_name__,
                version=__version__,
                description=__title__,
                include_package_data=True,
                long_description_content_type="text/markdown",
                long_description=readme,
                author=__author__,
                author_email=__author_email__,
                license=__license__,
                url=__url__,
                packages=find_packages(),
                python_requires=__python_requires__,
                install_requires=requirements,
                zip_safe=True,
                entry_points={
                    "console_scripts":
                    ["fastflyer = fastflyer.tools.entrypoint:main"],
                },
                classifiers=__classifiers__)

setup(**settings)
