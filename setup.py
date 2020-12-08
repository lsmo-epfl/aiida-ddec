#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setting up DDEC plugin for AiiDA"""
from __future__ import absolute_import
import json
from setuptools import setup, find_packages


def run_setup():
    """Set up aiida-ddec package"""
    with open('setup.json', 'r') as info:
        kwargs = json.load(info)
    setup(
        include_package_data=True,
        packages=find_packages(),
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        **kwargs
    )


if __name__ == '__main__':
    run_setup()
