# ============LICENSE_START=======================================================
# org.onap.dcae
# ================================================================================
# Copyright (c) 2017-2018 AT&T Intellectual Property. All rights reserved.
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
Tests component CLI commands
'''
import os
import json
from click.testing import CliRunner
import time
import pytest

from dcae_cli.cli import cli
from dcae_cli.catalog import MockCatalog

TEST_DIR = os.path.dirname(__file__)


def _get_spec(path):
    with open(path) as file:
        return json.load(file)


def test_comp_docker(mock_cli_config, mock_db_url, obj=None):

    obj = {'catalog': MockCatalog(purge_existing=True, db_name='dcae_cli.test.db',
        enforce_image=False, db_url=mock_db_url),
           'config': {'user': 'test-user'}}

    df_kpi = os.path.join(TEST_DIR, 'mocked_components', 'collector', 'vnf-kpi.format.json')
    comp_coll = os.path.join(TEST_DIR, 'mocked_components', 'collector', 'kpi-collector.comp.json')

    df_cls = os.path.join(TEST_DIR, 'mocked_components', 'model', 'int-class.format.json')
    comp_model = os.path.join(TEST_DIR, 'mocked_components', 'model', 'anomaly-model.comp.json')

    df_empty = os.path.join(TEST_DIR, 'mocked_components', 'viz', 'empty.format.json')
    df_url = os.path.join(TEST_DIR, 'mocked_components', 'viz', 'web-url.format.json')
    comp_viz = os.path.join(TEST_DIR, 'mocked_components', 'viz', 'line-viz.comp.json')

    runner = CliRunner()


    # add the collector
    cmd = "data_format add {:}".format(df_kpi).split()
    assert runner.invoke(cli, cmd, obj=obj).exit_code == 0

    cmd = "component add {:}".format(comp_coll).split()
    assert runner.invoke(cli, cmd, obj=obj).exit_code == 0


    # add the model
    cmd = "data_format add {:}".format(df_cls).split()
    assert runner.invoke(cli, cmd, obj=obj).exit_code == 0

    cmd = "component add {:}".format(comp_model).split()
    assert runner.invoke(cli, cmd, obj=obj).exit_code == 0


    # add the viz
    cmd = "data_format add {:}".format(df_empty).split()
    assert runner.invoke(cli, cmd, obj=obj).exit_code == 0

    cmd = "data_format add {:}".format(df_url).split()
    assert runner.invoke(cli, cmd, obj=obj).exit_code == 0

    cmd = "component add {:}".format(comp_viz).split()
    assert runner.invoke(cli, cmd, obj=obj).exit_code == 0


    # light test of component list
    df_cls_spec = _get_spec(df_cls)
    df_cls_name, df_cls_ver = df_cls_spec['self']['name'], df_cls_spec['self']['version']
    comp_model_spec = _get_spec(comp_model)
    comp_model_name = comp_model_spec['self']['name']

    cmd = "component list -pub {:}".format(df_cls_name).split()
    #assert comp_model_name in runner.invoke(cli, cmd, obj=obj).output

    cmd = "component list -pub {:}:{:}".format(df_cls_name, df_cls_ver).split()
    #assert comp_model_name in runner.invoke(cli, cmd, obj=obj).output


    # light test of component info
    cmd = "component show {:}".format(comp_model_name).split()
    spec_str = runner.invoke(cli, cmd, obj=obj).output
    assert comp_model_spec == json.loads(spec_str)


@pytest.mark.skip(reason="This is not a pure unit test. Need a way to setup dependencies and trigger in the appropriate stages of testing.")
def test_comp_cdap(obj=None):
    """
    This is not a unit test. It is bigger than that. It Does a full "workflow" test:
    1) adds a data format
    2) adds a cdap component
    3) runs a cdap component using our "Rework" broker
    4) undeploys the cdap component using our "Rework" broker

    NOTE: TODO: Mocking out the broker would be an improvement over this, probably. This is impure. Mocking the broker owuld be a huge undertaking, though.
    """

    obj = {'catalog': MockCatalog(purge_existing=True, db_name='dcae_cli.test.db'),
           'config': {'user': 'test-user'}}
    runner = CliRunner()

    #add the data format
    df = os.path.join(TEST_DIR, 'mocked_components', 'cdap', 'format.json')
    cmd = "data_format add {:}".format(df).split()
    assert runner.invoke(cli, cmd, obj=obj).exit_code == 0

    #add the CDAP components
    # TODO: Need to update the host
    jar = 'http://make-me-valid/HelloWorld-3.4.3.jar'

    comp_cdap_start = os.path.join(TEST_DIR, 'mocked_components', 'cdap', 'spec_start.json')
    cmd = "component add {0}".format(comp_cdap_start).split()
    print(cmd)
    result = runner.invoke(cli, cmd, obj=obj)
    print(result.output)
    assert result.exit_code == 0

    comp_cdap_end = os.path.join(TEST_DIR, 'mocked_components', 'cdap', 'spec_end.json')
    cmd = "component add {0}".format(comp_cdap_end).split()
    print(cmd)
    result = runner.invoke(cli, cmd, obj=obj)
    print(result.output)
    assert result.exit_code == 0

if __name__ == '__main__':
    '''Test area'''
    #pytest.main([__file__, ])
    test_comp_cdap()
