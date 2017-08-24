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
Tests data_format CLI commands
'''
import os
import json

import pytest
from click.testing import CliRunner

from dcae_cli.cli import cli
from dcae_cli.catalog import MockCatalog


TEST_DIR = os.path.dirname(__file__)


def _get_spec(path):
    with open(path) as file:
        return json.load(file)


def test_basic():

    obj = {'catalog': MockCatalog(purge_existing=True, db_name='dcae_cli.test.db', enforce_image=False),
           'config': {'user': 'test-user'}}

    runner = CliRunner()
    spec_file = os.path.join(TEST_DIR, 'mocked_components', 'model', 'int-class.format.json')
    cmd = "data_format add {:}".format(spec_file).split()

    # succeed the first time
    result = runner.invoke(cli, cmd, obj=obj)

    assert result.exit_code == 0

    # adding a duplicate is an error
    result = runner.invoke(cli, cmd, obj=obj)
    assert result.exit_code == 1
    assert 'exists' in result.output.lower()

    # allow updates
    cmd = "data_format add --update {:}".format(spec_file).split()
    result = runner.invoke(cli, cmd, obj=obj)
    assert result.exit_code == 0


    # light test of list format command
    cmd = 'data_format list'.split()
    df_spec = _get_spec(spec_file)
    df_name = df_spec['self']['name']
    assert df_name in runner.invoke(cli, cmd, obj=obj).output


    # light test of component info
    cmd = "data_format show {:}".format(df_name).split()
    spec_str = runner.invoke(cli, cmd, obj=obj).output
    assert df_spec == json.loads(spec_str)


if __name__ == '__main__':
    '''Test area'''
    pytest.main([__file__, ])
