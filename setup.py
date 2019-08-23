#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setting up DDEC plugin for AiiDA"""
from __future__ import absolute_import
import json
from setuptools import setup, find_packages

if __name__ == '__main__':
    # Provide static information in setup.json
    # such that it can be discovered automatically
    with open('setup.json', 'r') as info:
        kwargs = json.load(info)  # pylint: disable=invalid-name
    setup(packages=find_packages(), **kwargs)
