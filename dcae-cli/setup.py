# ============LICENSE_START=======================================================
# org.onap.dcae
# ================================================================================
# Copyright (c) 2017 AT&T Intellectual Property. All rights reserved.
# ================================================================================
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============LICENSE_END=========================================================
#
# ECOMP is a trademark and service mark of AT&T Intellectual Property.

# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


# extract __version__ from version file. importing dcae_cli will lead to install failures
setup_dir = os.path.dirname(__file__)
with open(os.path.join(setup_dir, 'dcae_cli', '_version.py')) as file:
    globals_dict = dict()
    exec(file.read(), globals_dict)
    __version__ = globals_dict['__version__']


setup(
    name = "onap-dcae-cli",
    version = __version__,
    packages = find_packages(),
    author = "Michael Hwang, Paul Triantafyllou, Tommy Carpenter",
    description = ("DCAE component on-boarding utility"),
    entry_points="""
    [console_scripts]
    dcae_cli=dcae_cli.cli:cli
    """,
    setup_requires=['pytest-runner'],
    install_requires=['python-consul',
                      'six',
                      'sqlalchemy',
                      'SQLAlchemy-Utils',
                      'click',
                      'jsonschema',
                      'terminaltables',
                      'psycopg2',
                      'genson',
                      'onap-dcae-discovery-client>=2.0.0',
                      'onap-dcae-dockering>=1.0.0,<2.0.0'
                      ],
    tests_require=['pytest',
                   'mock'],
    )
