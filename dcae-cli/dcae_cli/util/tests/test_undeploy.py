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
Provides tests for the undeploy module
'''
from dcae_cli.util.undeploy import _handler, _handler_report

def test_handler():
    instances = set(["some-instance-name", "another-instance-name"])

    def fake_remove_config(config_key):
        return True

    def undeploy_success(config_key):
        return True

    failures, results = _handler([undeploy_success, fake_remove_config], instances)

    assert len(results) == 2
    assert len(failures) == 0

    def undeploy_failure(config_key):
        return False

    failures, results = _handler([undeploy_failure, fake_remove_config], instances)

    assert len(results) == 2
    assert len(failures) == 2

    def undeploy_failure_sometimes(config_key):
        if "some-instance-name" == config_key:
            return False
        return True

    failures, results = _handler([undeploy_failure_sometimes, fake_remove_config], instances)

    assert len(results) == 2
    assert len(failures) == 1

    failures, results = _handler([undeploy_success, fake_remove_config], [])

    assert len(results) == 0
    assert len(failures) == 0
