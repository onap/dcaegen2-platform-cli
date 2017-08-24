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
"""
Provides profiles commands
"""
import json

import click

from dcae_cli.util.exc import DcaeException
from dcae_cli.util.profiles import (get_profiles, activate_profile, get_active_name, update_profile,
                                    delete_profile, create_profile)


@click.group()
def profiles():
    pass


@profiles.command()
@click.argument('name')
def activate(name):
    '''Sets profile NAME as the active profile'''
    activate_profile(name)


@profiles.command(name='list')
def list_profiles():
    '''Lists available profiles'''
    profiles = get_profiles(include_active=False)
    active = get_active_name()
    names = sorted(profiles.keys())
    outputs = ("{} {}".format('  ' if not name == active else '* ', name) for name in names)
    click.echo('\n'.join(outputs))


@profiles.command()
@click.argument('name')
def show(name):
    '''Prints the profile dictionary'''
    profiles = get_profiles()
    try:
        click.echo(json.dumps(profiles[name], sort_keys=True, indent=4))
    except KeyError as e:
        raise DcaeException("Profile '{}' does not exist.".format(e))


@profiles.command()
@click.argument('name', type=click.STRING)
def create(name):
    '''Creates a new profile NAME initialized with defaults'''
    create_profile(name)


@profiles.command(name='set')
@click.argument('name')
@click.argument('key')
@click.argument('value')
def update(name, key, value):
    '''Updates profile NAME such that KEY=VALUE'''
    update_profile(name, **{key: value})


@profiles.command()
@click.argument('name')
def delete(name):
    '''Deletes profile NAME'''
    delete_profile(name)
