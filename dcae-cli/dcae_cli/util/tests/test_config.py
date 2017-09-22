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
Tests the config functionality
"""
import os, json
from functools import partial
from mock import patch

import pytest
import click

import dcae_cli
from dcae_cli.util import config, write_pref
from dcae_cli.util.config import get_app_dir, get_config, get_config_path


def test_no_config(monkeypatch, tmpdir):
    '''Tests the creation and initialization of a config on a clean install'''
    monkeypatch.setattr(click, "get_app_dir", lambda app: str(tmpdir.realpath()))

    mock_config = {'user': 'mock-user'}

    config_file = tmpdir.join("config.json")
    config_file.write(json.dumps(mock_config))

    assert get_config() == mock_config


def test_init_config_user(monkeypatch):
    good_case = "abc123"
    values = [ good_case, "d-e-f", "g*h*i", "j k l" ]

    def fake_input(values, message, type="red"):
        return values.pop()

    monkeypatch.setattr(click, 'prompt', partial(fake_input, values))
    assert config._init_config_user() == good_case


def test_init_config(monkeypatch):
    monkeypatch.setattr(config, '_init_config_user', lambda: "bigmama")
    monkeypatch.setattr(config, '_init_config_server_url',
            lambda: "http://some-nexus-in-the-sky.com")
    monkeypatch.setattr(dcae_cli.util, 'fetch_file_from_web',
            lambda server_url, path: { "db_url": "conn" })
    monkeypatch.setattr("dcae_cli._version.__version__", "2.X.X")

    expected = {'cli_version': '2.X.X', 'user': 'bigmama', 'db_url': 'conn',
            'server_url': 'http://some-nexus-in-the-sky.com',
            'active_profile': 'default' }
    assert expected == config._init_config()

    # Test using of db fallback

    monkeypatch.setattr(dcae_cli.util, 'fetch_file_from_web',
            lambda server_url, path: { "db_url": "" })

    db_url = "postgresql://king:of@mountain:5432/dcae_onboarding_db"

    def fake_init_config_db_url():
        return db_url

    monkeypatch.setattr(config, "_init_config_db_url",
            fake_init_config_db_url)

    assert db_url == config._init_config()["db_url"]

    monkeypatch.setattr(dcae_cli.util, 'fetch_file_from_web',
            lambda server_url, path: {})

    assert db_url == config._init_config()["db_url"]

    # Simulate error trying to fetch

    def fetch_simulate_error(server_url, path):
        raise RuntimeError("Simulated error")

    monkeypatch.setattr(dcae_cli.util, 'fetch_file_from_web',
            fetch_simulate_error)
    # Case when user opts out of manually setting up
    monkeypatch.setattr(click, "confirm", lambda msg: False)

    with pytest.raises(config.ConfigurationInitError):
        config._init_config()


def test_should_force_reinit():
    bad_config = {}
    assert config.should_force_reinit(bad_config) == True

    old_config = { "cli_version": "1.0.0" }
    assert config.should_force_reinit(old_config) == True

    uptodate_config = { "cli_version": "2.0.0" }
    assert config.should_force_reinit(uptodate_config) == False


def test_reinit_config(monkeypatch, tmpdir):
    monkeypatch.setattr(click, "get_app_dir", lambda app: str(tmpdir.realpath()))

    new_config = { "user": "ninny", "db_url": "some-db" }

    def init():
        return new_config

    assert config._reinit_config(init) == new_config

    old_config = { "user": "super", "db_url": "other-db", "hidden": "yo" }
    write_pref(old_config, get_config_path())

    new_config["hidden"] = "yo"
    assert config._reinit_config(init) == new_config


if __name__ == '__main__':
    '''Test area'''
    pytest.main([__file__, ])
