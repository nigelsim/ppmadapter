#!/usr/bin/env python
from setuptools import setup

# Uses the config from setup.cfg by invoking d2to1
setup(setup_requires=['d2to1'], d2to1=True)
