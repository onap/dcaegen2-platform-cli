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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Provides dcae cli profile variables
"""
import os
from collections import namedtuple

import six
import click

from dcae_cli import util
from dcae_cli.util import get_app_dir, get_pref, write_pref
from dcae_cli.util import config
from dcae_cli.util.config import get_config, update_config
from dcae_cli.util.exc import DcaeException
from dcae_cli.util.logger import get_logger


logger = get_logger('Profile')


# reserved profile names
ACTIVE = 'active'
_reserved_names = {ACTIVE}


# create enums for profile keys so that they can be imported for testing, instead of using literals
CONSUL_HOST = 'consul_host'
CONFIG_BINDING_SERVICE = 'config_binding_service'
CDAP_BROKER = 'cdap_broker'
DOCKER_HOST = 'docker_host'

# TODO: Should probably lift this strict list of allowed keys and repurpose to be
# keys that are required.
_allowed_keys = set([CONSUL_HOST, CONFIG_BINDING_SERVICE, CDAP_BROKER, DOCKER_HOST])
Profile = namedtuple('Profile', _allowed_keys)


def _create_stub_profile():
    """Create a new stub of a profile"""
    return { k: "" for k in _allowed_keys }


def _fmt_seq(seq):
    '''Returns a sorted string formatted list'''
    return list(sorted(map(str, seq)))


def get_profiles_path():
    '''Returns the absolute path to the profiles file'''
    return os.path.join(get_app_dir(), 'profiles.json')


def get_active_name():
    '''Returns the active profile name in the config'''
    return config.get_active_profile()


def _set_active_name(name):
    '''Sets the active profile name in the config'''
    update_config(active_profile=name)


class ProfilesInitError(RuntimeError):
    pass

def reinit_profiles():
    """Reinitialize profiles

    Grab the remote profiles and merge with the local profiles if there is one.

    Returns:
    --------
    Dict of complete new profiles
    """
    # Grab the remote profiles and merge it in
    try:
        server_url = config.get_server_url()
        new_profiles = util.fetch_file_from_web(server_url, "/dcae-cli/profiles.json")
    except:
        # Failing to pull seed profiles from remote server is not considered
        # a problem. Just continue and give user the option to use an empty
        # default.
        if click.confirm("Could not download initial profiles from remote server. Set empty default?"):
            new_profiles = {"default": { "consul_host": "",
                "config_binding_service": "config_binding_service",
                "cdap_broker": "cdap_broker", "docker_host": ""}}
        else:
            raise ProfilesInitError("Could not setup dcae-cli profiles")

    profiles_path = get_profiles_path()

    if  util.pref_exists(profiles_path):
        existing_profiles = get_profiles(include_active=False)
        # Make sure to clobber existing values and not other way
        existing_profiles.update(new_profiles)
        new_profiles = existing_profiles

    write_pref(new_profiles, profiles_path)
    return new_profiles


def get_profiles(user_only=False, include_active=True):
    '''Returns a dict containing all available profiles

    Example of the returned dict:
        {
            "profile-foo": {
                "some_variable_A": "some_value_A",
                "some_variable_B": "some_value_B",
                "some_variable_C": "some_value_C"
            }
        }
    '''
    try:
        profiles = get_pref(get_profiles_path(), reinit_profiles)
    except ProfilesInitError as e:
        raise DcaeException("Failed to initialize profiles: {0}".format(e))

    if user_only:
        return profiles

    if include_active:
        active_name = get_active_name()
        if active_name not in profiles:
            raise DcaeException("Active profile '{}' does not exist. How did this happen?".format(active_name))
        profiles[ACTIVE] = profiles[active_name]

    return profiles


def get_profile(name=ACTIVE):
    '''Returns a `Profile` object'''
    profiles = get_profiles()

    if name not in profiles:
        raise DcaeException("Specified profile '{}' does not exist.".format(name))

    try:
        profile = Profile(**profiles[name])
    except TypeError as e:
        raise DcaeException("Specified profile '{}' is malformed.".format(name))

    return profile


def create_profile(name, **kwargs):
    '''Creates a new profile'''
    _assert_not_reserved(name)

    profiles = get_profiles(user_only=True)
    if name in profiles:
        raise DcaeException("Profile '{}' already exists.".format(name))

    profile = _create_stub_profile()
    profile.update(kwargs)
    _assert_valid_profile(profile)

    profiles[name] = profile
    _write_profiles(profiles)


def delete_profile(name):
    '''Deletes a profile'''
    _assert_not_reserved(name)
    profiles = get_profiles(user_only=True)
    if name not in profiles:
        raise DcaeException("Profile '{}' does not exist.".format(name))
    if name == get_active_name():
        logger.warning("Profile '{}' is currently active. Activate another profile first."
                .format(name))
        return False
    del profiles[name]
    _write_profiles(profiles)
    return True


def update_profile(name, **kwargs):
    '''Creates or updates a profile'''
    _assert_not_reserved(name)
    _assert_valid_profile(kwargs)

    profiles = get_profiles(user_only=True)
    if name not in profiles:
        raise DcaeException("Profile '{}' does not exist.".format(name))

    profiles[name].update(kwargs)
    _write_profiles(profiles)


def _assert_valid_profile(params):
    '''Raises DcaeException if the profile parameter dict is invalid'''
    if not params:
        raise DcaeException('No update key-value pairs were provided.')
    keys = set(params.keys())
    if not _allowed_keys.issuperset(keys):
        invalid_keys = keys - _allowed_keys
        raise DcaeException("Invalid keys {} detected. Only keys {} are supported.".format(_fmt_seq(invalid_keys), _fmt_seq(_allowed_keys)))


def _assert_not_reserved(name):
    '''Raises DcaeException if the profile is reserved'''
    if name in _reserved_names:
        raise DcaeException("Profile '{}' is reserved and cannot be modified.".format(name))


def _write_profiles(profiles):
    '''Writes the profiles dictionary to disk'''
    return write_pref(profiles, path=get_profiles_path())


def activate_profile(name):
    '''Modifies the config and sets a new active profile'''
    avail_profiles = set(get_profiles().keys()) - {ACTIVE, }
    if name not in avail_profiles:
        raise DcaeException("Profile name '{}' does not exist. Please select from {} or create a new profile.".format(name, _fmt_seq(avail_profiles)))
    _set_active_name(name)
