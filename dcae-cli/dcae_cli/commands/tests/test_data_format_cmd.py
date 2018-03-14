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


def test_basic(mock_cli_config, mock_db_url, tmpdir):
    obj = {'catalog': MockCatalog(purge_existing=True, db_name='dcae_cli.test.db', 
        enforce_image=False, db_url=mock_db_url),
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

    # test of generate
    bad_dir = os.path.join(TEST_DIR, 'mocked_components', 'model', 'baddir')
    cmd = "data_format generate --keywords \"name:1.0.2\" {:}".format(bad_dir).split()
    err_str = runner.invoke(cli, cmd, obj=obj).output
    assert "does not exist" in err_str 

    empty_dir = os.path.join(TEST_DIR, 'mocked_components', 'model', 'emptydir')
    try:
      os.stat(empty_dir)
    except:
      os.mkdir(empty_dir)
    cmd = "data_format generate --keywords \"name:1.0.2\" {:}".format(empty_dir).split()
    err_str = runner.invoke(cli, cmd, obj=obj).output
    assert "No JSON files found" in err_str 

    bad_json = os.path.join(TEST_DIR, 'mocked_components', 'model', 'badjson')
    cmd = "data_format generate --keywords \"name:1.0.2\" {:}".format(bad_json).split()
    err_str = runner.invoke(cli, cmd, obj=obj).output
    assert "Bad JSON file" in err_str 

    generate_dir = os.path.join(TEST_DIR, 'mocked_components', 'model', 'generatedir')
    cmd = "data_format generate --keywords name:1.0.2 {:} ".format(generate_dir).split()
    actual = json.loads(runner.invoke(cli, cmd, obj=obj).output)
    expected = json.loads('{\n    "dataformatversion": "1.0.0", \n    "jsonschema": {\n        "$schema": "http://json-schema.org/draft-04/schema#", \n        "description": "", \n        "properties": {\n            "foobar": {\n                "description": "", \n                "maxLength": 0, \n                "minLength": 0, \n                "pattern": "", \n                "type": "string"\n            }, \n            "foobar2": {\n                "description": "", \n                "maxLength": 0, \n                "minLength": 0, \n                "pattern": "", \n                "type": "string"\n            }\n        }, \n        "type": "object"\n    }, \n    "self": {\n        "description": "", \n        "name": "name", \n        "version": "1.0.2"\n    }\n}\n')
    assert actual == expected

    generate_dir = os.path.join(TEST_DIR, 'mocked_components', 'model', 'generatedir')
    cmd = "data_format generate name:1.0.2 {:} ".format(generate_dir).split()
    actual = json.loads(runner.invoke(cli, cmd, obj=obj).output)
    expected = json.loads('{\n    "dataformatversion": "1.0.0", \n    "jsonschema": {\n        "$schema": "http://json-schema.org/draft-04/schema#", \n        "description": "", \n        "properties": {\n            "foobar": {\n                "description": "", \n                "type": "string"\n            }, \n            "foobar2": {\n                "description": "", \n                "type": "string"\n            }\n        }, \n        "type": "object"\n    }, \n    "self": {\n        "description": "", \n        "name": "name", \n        "version": "1.0.2"\n    }\n}\n'
            )
    assert actual == expected

    generate_dir = os.path.join(TEST_DIR, 'mocked_components', 'model', 'generatedir', 'ex1.json')
    cmd = "data_format generate name:1.0.2 {:} ".format(generate_dir).split()
    actual = json.loads(runner.invoke(cli, cmd, obj=obj).output)
    expected = json.loads('{\n    "dataformatversion": "1.0.0", \n    "jsonschema": {\n        "$schema": "http://json-schema.org/draft-04/schema#", \n        "additionalproperties": true, \n        "description": "", \n        "properties": {\n            "foobar": {\n                "description": "", \n                "type": "string"\n            }\n        }, \n        "required": [\n            "foobar"\n        ], \n        "type": "object"\n    }, \n    "self": {\n        "description": "", \n        "name": "name", \n        "version": "1.0.2"\n    }\n}\n')
    assert actual == expected


if __name__ == '__main__':
    '''Test area'''
    pytest.main([__file__, ])
