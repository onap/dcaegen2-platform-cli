# ============LICENSE_START=======================================================
# org.onap.dcae
# ================================================================================
# Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
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
"""
This module is actually for pytesting. This contains fixtures.
"""

import pytest
import dcae_cli

# REVIEW: Having issues trying to share this amongst all the tests. Putting this
# fixture here allows it to be shared when running tests over the entire project.
# The pytest recommendation was to place this file high up in the project.

@pytest.fixture
def mock_cli_config(monkeypatch):
    """Fixture to provide a mock dcae-cli configuration and profiles

    This fixture monkeypatches the respective get calls to return mock objects
    """
    fake_config = { "active_profile": "default", "user": "bob",
            "server_url": "https://git.onap.org/dcaegen2/platform/cli/plain",
            "db_url": "postgresql://postgres:abc123@localhost:5432/dcae_onboarding_db"
            }

    fake_profiles = { "default": { "consul_host": "consul",
        "cdap_broker": "cdap_broker",
        "config_binding_service": "config_binding_service",
        "docker_host": "docker_host" }
        }
    fake_profiles["active"] = fake_profiles["default"]

    def fake_get_config():
        return fake_config

    def fake_get_profiles(user_only=False, include_active=True):
        return fake_profiles

    from dcae_cli.util import config, profiles
    monkeypatch.setattr(dcae_cli.util.config, "get_config", fake_get_config)
    monkeypatch.setattr(dcae_cli.util.profiles, "get_profiles", fake_get_profiles)


@pytest.fixture
def mock_db_url(tmpdir):
    """Fixture to provide mock db url

    This url is intended to be the location of where to place the local sqlite
    databases for each unit test"""
    dbname="dcae_cli.test.db"
    config_dir = tmpdir.mkdir("config")
    return "/".join(["sqlite://", str(config_dir), dbname])
