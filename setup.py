#!/usr/bin/env python3
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages


NAME = 'wazo-setupd'
setup(
    name=NAME,
    version='1.0',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    packages=find_packages(),
    package_data={'wazo_setupd.plugins': ['*/api.yml']},
    entry_points={
        'console_scripts': [
            '{}=wazo_setupd.main:main'.format(NAME),
        ],
        'wazo_setupd.plugins': [
            'api = wazo_setupd.plugins.api.plugin:Plugin',
            'config = wazo_setupd.plugins.config.plugin:Plugin',
            'setup = wazo_setupd.plugins.setup.plugin:Plugin',
            'status = wazo_setupd.plugins.status.plugin:Plugin',
        ],
    },
)
