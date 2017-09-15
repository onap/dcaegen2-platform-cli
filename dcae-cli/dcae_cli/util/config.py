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
Provides dcae cli config utilities
"""
import os, re

import click
import six

from dcae_cli import util
from dcae_cli import _version
from dcae_cli.util import get_app_dir, get_pref, update_pref, write_pref, pref_exists


class ConfigurationInitError(RuntimeError):
    pass

def get_config_path():
    '''Returns the absolute configuration file path'''
    return os.path.join(get_app_dir(), 'config.json')


def _init_config_user():
    while True:
        user = click.prompt('Please enter your user id', type=str).strip()

        # There should be no special characters
        if re.match("(?:\w*)\Z", user):
            return user
        else:
            click.echo("Invalid user id. Please try again.")

def _init_config_server_url():
    return click.prompt('Please enter the remote server url', type=str).strip()

def _init_config():
    '''Returns an initial dict for populating the config'''
    # Grab the remote config and merge it in
    try:
        server_url = _init_config_server_url()
        new_config = util.fetch_file_from_web(server_url, "/dcae-cli/config.json")
        new_config["server_url"] = server_url
    except:
        # REVIEW: Should we allow users to manually setup their config if not
        # able to pull from remote server?
        raise ConfigurationInitError("Could not download configuration from remote server")

    new_config["user"] = _init_config_user()
    new_config["cli_version"] = _version.__version__

    if "db_url" not in new_config or not new_config["db_url"]:
        # Really you should never get to this point because the remote config
        # should have a postgres db url.
        fallback = ''.join(('sqlite:///', os.path.join(get_app_dir(), 'dcae_cli.db')))
        new_config["db_url"] = fallback

    return new_config


def should_force_reinit(config):
    """Configs older than 2.0.0 should be replaced"""
    ver = config.get("cli_version", "0.0.0")
    return int(ver.split(".")[0]) < 2

def get_config():
    '''Returns the configuration dictionary'''
    return get_pref(get_config_path(), _init_config)

def get_server_url():
    """Returns the remote server url

    The remote server holds the artifacts that the dcae-cli requires like the
    seed config json and seed profiles json, and json schemas.
    """
    return get_config().get("server_url")

# These functions are used to fetch the configurable path to the various json
# schema files used in validation.

def get_path_component_spec():
    return get_config().get("path_component_spec",
            "/schemas/component-specification/dcae-cli-v1/component-spec-schema.json")

def get_path_data_format():
    return get_config().get("path_data_format",
            "/schemas/data-format/dcae-cli-v1/data-format-schema.json")

def get_active_profile():
    return get_config().get("active_profile", None)


def update_config(**kwargs):
    '''Updates and returns the configuration dictionary'''
    return update_pref(path=get_config_path(), init_func=get_config, **kwargs)


def _reinit_config(init_func):
    new_config = init_func()
    config_path = get_config_path()

    if  pref_exists(config_path):
        existing_config = get_config()
        # Make sure to clobber existing values and not other way
        existing_config.update(new_config)
        new_config = existing_config

    write_pref(new_config, config_path)
    return new_config

def reinit_config():
    return _reinit_config(_init_config)
