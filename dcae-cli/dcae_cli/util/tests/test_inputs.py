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

"""
Tests for inputs module
"""
import pytest
from dcae_cli.util import inputs


def test_filter_entries():
    spec = { "parameters": [{"name": "foo"}, {"name": "bar",
        "sourced_at_deployment": False}, {"name": "baz", "sourced_at_deployment": True}] }

    with pytest.raises(inputs.InputsValidationError):
        inputs.filter_entries({}, spec)

    inputs_map = { "foo": "do not copy", "baz": "hello world", "extra": "do not copy" }

    assert len(inputs.filter_entries(inputs_map, spec)) == 1
