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
Tests the profiles module
"""
import os, json, copy
from functools import partial

import click
import pytest

from dcae_cli import util
from dcae_cli.util.exc import DcaeException
from dcae_cli.util import profiles
from dcae_cli.util.profiles import (get_active_name, get_profile, get_profiles, get_profiles_path,
                                    create_profile, delete_profile, update_profile, ACTIVE,
                                    activate_profile, CONSUL_HOST)
from dcae_cli.util import config


def test_profiles(monkeypatch, tmpdir):
    '''Tests the creation and initialization of profiles on a clean install'''
    # Setup config
    config_dict = { "active_profile": "fake-solutioning", "db_url": "some-db" }
    config_file = tmpdir.join("config.json")
    config_file.write(json.dumps(config_dict))

    # Setup profile
    profile_dict = { "fake-solutioning": { "cdap_broker": "cdap_broker",
        "config_binding_service": "config_binding_service",
        "consul_host": "realsolcnsl00.dcae.solutioning.com",
        "docker_host": "realsoldokr00.dcae.solutioning.com:2376" }}
    profile_file = tmpdir.join("profiles.json")
    profile_file.write(json.dumps(profile_dict))

    monkeypatch.setattr(click, "get_app_dir", lambda app: str(tmpdir.realpath()))

    assert get_active_name() == config_dict["active_profile"]
    assert get_profile() == profiles.Profile(**profile_dict["fake-solutioning"])

    # Failures looking for unknown profile

    with pytest.raises(DcaeException):
        get_profile('foo')

    with pytest.raises(DcaeException):
        delete_profile('foo')

    with pytest.raises(DcaeException):
        update_profile('foo', **{})  # doesn't exist

    # Cannot delete active profile

    assert delete_profile(get_active_name()) == False

    # Do different get_profiles queries

    assert get_profiles(user_only=True) == profile_dict
    all_profiles = copy.deepcopy(profile_dict)
    all_profiles[ACTIVE] = profile_dict["fake-solutioning"]
    assert get_profiles(user_only=False) == all_profiles

    # Create and activate new profile

    create_profile('foo')
    activate_profile('foo')
    assert get_active_name() == 'foo'

    # Update new profile

    update_profile('foo', **{CONSUL_HOST:'bar'})
    assert get_profiles()['foo'][CONSUL_HOST] == 'bar'
    assert get_profile()._asdict()[CONSUL_HOST] == 'bar'

    activate_profile("fake-solutioning")
    assert delete_profile('foo') == True


def test_reinit_via_get_profiles(monkeypatch, tmpdir):
    monkeypatch.setattr(click, "get_app_dir", lambda app: str(tmpdir.realpath()))

    def fake_reinit_failure():
        raise profiles.ProfilesInitError("Faked failure")

    monkeypatch.setattr(profiles, "reinit_profiles", fake_reinit_failure)

    with pytest.raises(DcaeException):
        get_profiles()


def test_reinit_profiles(monkeypatch, tmpdir):
    monkeypatch.setattr(click, "get_app_dir", lambda app: str(tmpdir.realpath()))

    # Setup config (need this because the "active_profile" is needed)
    config_dict = { "active_profile": "fake-solutioning", "db_url": "some-db" }
    config_file = tmpdir.join("config.json")
    config_file.write(json.dumps(config_dict))

    # Start with empty profiles

    profile_dict = { "fake-solutioning": { "cdap_broker": "cdap_broker",
        "config_binding_service": "config_binding_service",
        "consul_host": "realsolcnsl00.dcae.solutioning.com",
        "docker_host": "realsoldokr00.dcae.solutioning.com:2376" }}

    def fetch_profile(target_profile, server_url, path):
        return target_profile

    monkeypatch.setattr(util, "fetch_file_from_web", partial(fetch_profile,
        profile_dict))
    profiles.reinit_profiles()
    assert profiles.get_profiles(include_active=False) == profile_dict

    # Test update

    profile_dict = { "fake-5g": { "cdap_broker": "cdap_broker",
        "config_binding_service": "config_binding_service",
        "consul_host": "realsolcnsl00.dcae.solutioning.com",
        "docker_host": "realsoldokr00.dcae.solutioning.com:2376" }}

    monkeypatch.setattr(util, "fetch_file_from_web", partial(fetch_profile,
        profile_dict))
    profiles.reinit_profiles()
    all_profiles = profiles.get_profiles(include_active=False)
    assert "fake-5g" in all_profiles
    assert "fake-solutioning" in all_profiles

    # Test fetch failure

    def fetch_failure(server_url, path):
        raise RuntimeError("Mysterious error")

    monkeypatch.setattr(util, "fetch_file_from_web", fetch_failure)
    # Case when user opts out of manually setting up
    monkeypatch.setattr(click, "confirm", lambda msg: False)

    with pytest.raises(profiles.ProfilesInitError):
        profiles.reinit_profiles()


if __name__ == '__main__':
    '''Test area'''
    pytest.main([__file__, ])
