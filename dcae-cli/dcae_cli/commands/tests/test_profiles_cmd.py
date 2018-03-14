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
'''
Tests profiles CLI commands
'''
import json

import pytest
import click
from click.testing import CliRunner

from dcae_cli import util
from dcae_cli.cli import cli
from dcae_cli.util import profiles
from dcae_cli.util import config


def test_basic(monkeypatch, tmpdir, mock_db_url):

    runner = CliRunner()

    # Setup config
    test_db_url = mock_db_url
    config_dict = { "user": "ninny", "active_profile": "fake-solutioning",
            "db_url": test_db_url, "cli_version": "2.0.0" }
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

    cmd = 'profiles show fake-solutioning'.split()
    result = runner.invoke(cli, cmd)
    assert result.output == "{}\n".format(json.dumps(profile_dict["fake-solutioning"],
        sort_keys=True, indent=4))

    cmd = 'profiles list'.split()
    result = runner.invoke(cli, cmd)
    assert result.output == '*  fake-solutioning\n'

    cmd = 'profiles create foo'.split()
    result = runner.invoke(cli, cmd)

    cmd = 'profiles list'.split()
    result = runner.invoke(cli, cmd)
    assert result.output == '*  fake-solutioning\n   foo\n'

    cmd = 'profiles activate foo'.split()
    result = runner.invoke(cli, cmd)

    cmd = 'profiles list'.split()
    result = runner.invoke(cli, cmd)
    assert result.output == '   fake-solutioning\n*  foo\n'


if __name__ == '__main__':
    '''Test area'''
    pytest.main([__file__, ])
