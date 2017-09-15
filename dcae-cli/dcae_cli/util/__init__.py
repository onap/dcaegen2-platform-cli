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
Provides reusable utilites
"""
import os
import json
import sys
import errno
import contextlib
import requests

import six
import click

from dcae_cli.util.exc import DcaeException, FileNotFoundError


APP_NAME = 'dcae-cli'


def get_app_dir():
    '''Returns the absolute directory path for dcae cli aux files'''
    return click.get_app_dir(APP_NAME)


def makedirs(path, exist_ok=True):
    '''Emulates Python 3.2+ os.makedirs functionality'''
    try:
        os.makedirs(path, exist_ok=exist_ok)
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno == errno.EEXIST and not exist_ok:
                raise


def get_pref(path, init_func=None):
    '''Returns a general preference dict. Uses `init_func` to create a new one if the file does not exist.'''
    try:
        with open(path) as file:
            pref = json.load(file)
    except FileNotFoundError:
        pref = init_func() if init_func is not None else dict()
        write_pref(pref, path)
    return pref


def pref_exists(path):
    return os.path.isfile(path)


def update_pref(path, init_func=None, **kwargs):
    '''Sets specified key-value pairs in a preference file and returns an updated dict'''
    pref = get_pref(path, init_func)
    pref.update(kwargs)
    write_pref(pref, path)

    return pref


def write_pref(pref, path):
    '''Writes a preference json file to disk'''
    makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as file:
        json.dump(pref, file)


def reraise_with_msg(e, msg=None, cls=None, as_dcae=False):
    '''Reraises exception e with an additional message prepended'''
    if as_dcae:
        cls = DcaeException
    traceback = sys.exc_info()[2]
    cls = e.__class__ if cls is None else cls
    new_msg = "{:}: {:}".format(msg, e) if msg else str(e)
    new_e = cls(new_msg)
    six.reraise(cls, new_e, traceback)


def load_json(path):
    '''Helper function which loads a JSON file and returns a dict'''
    with open(path) as file:
        try:
            return json.load(file)
        except ValueError:
            raise DcaeException("File '{}' appears to be a malformed JSON.".format(path))


def fetch_file_from_web(server_url, path, transform_func=json.loads):
    """Fetch file from a web server

    The default behavior is to transform the response to a json.
    """
    artifact_url = "{0}/{1}".format(server_url, path)
    r = requests.get(artifact_url)
    r.raise_for_status()
    if transform_func:
        return transform_func(r.text)
    else:
        return r.text
