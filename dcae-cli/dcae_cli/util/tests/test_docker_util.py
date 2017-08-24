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
Provides tests for the docker_util module
'''
import pytest
from dcae_cli.util.profiles import Profile, CONSUL_HOST, CONFIG_BINDING_SERVICE, CDAP_BROKER, DOCKER_HOST
from dcae_cli.util import docker_util as du


# TODO: formalize tests
'''
from dcae_cli.util.logger import set_verbose
set_verbose()

client = _get_docker_client()

params = dict()
interface_map = dict()
instance_map = dict()
# TODO: make-me-valid?
external_ip ='196.207.143.209'

# TODO: Need to replace the use of asimov
_run_component('asimov-anomaly-viz:0.0.0',
               'bob', 'asimov.anomaly.viz', '1.0.0', params, interface_map, instance_map,
               external_ip)
'''

def test_convert_profile_to_docker_envs():
    expected = { CONSUL_HOST.upper(): "some.consul.somewhere",
                 CONFIG_BINDING_SERVICE.upper(): "some.config_binding.somewhere",
                 CDAP_BROKER.upper(): "broker",
                 DOCKER_HOST.upper(): "some-docker-host"
               }
    profile = Profile(**{ CONSUL_HOST: expected[CONSUL_HOST.upper()],
                          CONFIG_BINDING_SERVICE: expected[CONFIG_BINDING_SERVICE.upper()],
                          CDAP_BROKER: expected[CDAP_BROKER.upper()],
                          DOCKER_HOST: expected[DOCKER_HOST.upper()]
                        })
    actual = du._convert_profile_to_docker_envs(profile)

    assert actual == expected
