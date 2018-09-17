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
Tests the mock catalog
'''
import json
from copy import deepcopy
from functools import partial

import pytest

from sqlalchemy.exc import IntegrityError

from dcae_cli.catalog.mock.catalog import MockCatalog, MissingEntry, DuplicateEntry, _get_unique_format_things
from dcae_cli.catalog.mock import catalog


_c1_spec = {'self': {'name': 'std.comp_one',
                    'version': '1.0.0',
                    'description': 'comp1',
                    'component_type': 'docker'},
          'streams': {'publishes': [{'format': 'std.format_one',
                                     'version': '1.0.0',
                                     'config_key': 'pub1',
                                     'type': 'http'}],
                      'subscribes': [{'format': 'std.format_one',
                                      'version': '1.0.0',
                                      'route': '/sub1',
                                      'type': 'http'}]},
          'services': {'calls': [{'request': {'format': 'std.format_one',
                                              'version': '1.0.0'},
                                  'response': {'format': 'std.format_one',
                                               'version': '1.0.0'},
                                  'config_key': 'call1'}],
                       'provides': [{'request': {'format': 'std.format_one',
                                                 'version': '1.0.0'},
                                     'response': {'format': 'std.format_one',
                                                  'version': '1.0.0'},
                                     'route': '/prov1'}]},
          'parameters': [{"name": "foo",
                          "value": 1,
                          "description": "the foo thing",
                          "designer_editable": False,
                          "sourced_at_deployment": False,
                          "policy_editable": False},
                         {"name": "bar",
                          "value": 2,
                          "description": "the bar thing",
                          "designer_editable": False,
                          "sourced_at_deployment": False,
                          "policy_editable": False}
                          ],
          'artifacts': [{ "uri": "foo-image", "type": "docker image" }],
          'auxilary': {
            "healthcheck": {
                "type": "http",
                "endpoint": "/health",
                "interval": "15s",
                "timeout": "1s"
                }
              }
           }

_c2_spec = {'self': {'name': 'std.comp_two',
                          'version': '1.0.0',
                          'description': 'comp2',
                          'component_type': 'docker'},
          'streams': {'publishes': [],
                      'subscribes': [{'format': 'std.format_one',
                                      'version': '1.0.0',
                                      'route': '/sub1',
                                      'type': 'http'}]},
          'services': {'calls': [],
                       'provides': [{'request': {'format': 'std.format_one',
                                                 'version': '1.0.0'},
                                     'response': {'format': 'std.format_one',
                                                  'version': '1.0.0'},
                                     'route': '/prov1'}]},
          'parameters': [],
          'artifacts': [{ "uri": "bar-image", "type": "docker image" }],
          'auxilary': {
            "healthcheck": {
                "type": "http",
                "endpoint": "/health",
                "interval": "15s",
                "timeout": "1s"
                }
              }
           }


_c2v2_spec = {'self': {'name': 'std.comp_two',
                          'version': '2.0.0',
                          'description': 'comp2',
                          'component_type': 'docker'},
          'streams': {'publishes': [],
                      'subscribes': [{'format': 'std.format_one',
                                      'version': '1.0.0',
                                      'route': '/sub1',
                                      'type': 'http'}]},
          'services': {'calls': [],
                       'provides': [{'request': {'format': 'std.format_one',
                                                 'version': '1.0.0'},
                                     'response': {'format': 'std.format_one',
                                                  'version': '1.0.0'},
                                     'route': '/prov1'}]},
          'parameters': [],
          'artifacts': [{ "uri": "baz-image", "type": "docker image" }],
          'auxilary': {
            "healthcheck": {
                "type": "http",
                "endpoint": "/health",
                "interval": "15s",
                "timeout": "1s"
                }
              }
           }


_c3_spec = {'self': {'name': 'std.comp_three',
                          'version': '3.0.0',
                          'description': 'comp3',
                          'component_type': 'docker'},
          'streams': {'publishes': [],
                      'subscribes': [{'format': 'std.format_two',
                                      'version': '1.5.0',
                                      'route': '/sub1',
                                      'type': 'http'}]},
          'services': {'calls': [],
                       'provides': [{'request': {'format': 'std.format_one',
                                                 'version': '1.0.0'},
                                     'response': {'format': 'std.format_two',
                                                  'version': '1.5.0'},
                                     'route': '/prov1'}]},
          'parameters': [],
          'artifacts': [{ "uri": "bazinga-image", "type": "docker image" }],
          'auxilary': {
            "healthcheck": {
                "type": "http",
                "endpoint": "/health",
                "interval": "15s",
                "timeout": "1s"
                }
              }
           }


_df1_spec = {
          "self": {
              "name": "std.format_one",
              "version": "1.0.0",
              "description": "df1"
          },
          "dataformatversion": "1.0.0",
          "jsonschema": {
              "$schema": "http://json-schema.org/draft-04/schema#",
                      "type": "object",
              "properties": {
                  "raw-text": {
                      "type": "string"
                  }
              },
              "required": ["raw-text"],
              "additionalProperties": False
          }
        }
_df2_spec = {
          "self": {
              "name": "std.format_two",
              "version": "1.5.0",
              "description": "df2"
          },
          "dataformatversion": "1.0.0",
          "jsonschema": {
              "$schema": "http://json-schema.org/draft-04/schema#",
                      "type": "object",
              "properties": {
                  "raw-text": {
                      "type": "string"
                  }
              },
              "required": ["raw-text"],
              "additionalProperties": False
          }
       }
_df2v2_spec  = {
          "self": {
              "name": "std.format_two",
              "version": "2.0.0",
              "description": "df2"
          },
          "dataformatversion": "1.0.0",
          "jsonschema": {
              "$schema": "http://json-schema.org/draft-04/schema#",
                      "type": "object",
              "properties": {
                  "raw-text": {
                      "type": "string"
                  }
              },
              "required": ["raw-text"],
              "additionalProperties": False
          }
            }

_cdap_spec={
   "self":{
      "name":"std.cdap_comp",
      "version":"0.0.0",
      "description":"cdap test component",
      "component_type":"cdap"
   },
   "streams":{
      "publishes":[
         {
            "format":"std.format_one",
            "version":"1.0.0",
            "config_key":"pub1",
            "type": "http"
         }
      ],
      "subscribes":[
         {
            "format":"std.format_two",
            "version":"1.5.0",
            "route":"/sub1",
            "type": "http"
         }
      ]
   },
   "services":{
      "calls":[

      ],
      "provides":[
         {
            "request":{
               "format":"std.format_one",
               "version":"1.0.0"
            },
            "response":{
               "format":"std.format_two",
               "version":"1.5.0"
            },
            "service_name":"baphomet",
            "service_endpoint":"rises",
            "verb":"GET"
         }
      ]
   },
   "parameters": {
       "app_config" : [],
       "app_preferences" : [],
       "program_preferences" : []
   },
   "artifacts": [{"uri": "bahpomet.com", "type": "jar"}],
   "auxilary": {
        "streamname":"streamname",
        "artifact_version":"6.6.6",
        "artifact_name": "test_name",
        "programs" : [{"program_type" : "flows", "program_id" : "flow_id"}]
        }

}


def test_component_basic(mock_cli_config, mock_db_url, catalog=None):
    '''Tests basic component usage of MockCatalog'''
    if catalog is None:
        mc = MockCatalog(db_name='dcae_cli.test.db', purge_existing=True,
                enforce_image=False, db_url=mock_db_url)
    else:
        mc = catalog

    c1_spec = deepcopy(_c1_spec)
    df1_spec = deepcopy(_df1_spec)
    df2_spec = deepcopy(_df2_spec)

    user = "test_component_basic"

    # success
    mc.add_format(df2_spec, user)

    # duplicate
    with pytest.raises(DuplicateEntry):
        mc.add_format(df2_spec, user)

    # component relies on df1_spec which hasn't been added
    with pytest.raises(MissingEntry):
        mc.add_component(user, c1_spec)

    # add df1 and comp1
    mc.add_format(df1_spec, user)
    mc.add_component(user, c1_spec)

    with pytest.raises(DuplicateEntry):
        mc.add_component(user, c1_spec)

    cname, cver = mc.verify_component('std.comp_one', version=None)
    assert cver == '1.0.0'


def test_format_basic(mock_cli_config, mock_db_url, catalog=None):
    '''Tests basic data format usage of MockCatalog'''
    if catalog is None:
        mc = MockCatalog(db_name='dcae_cli.test.db', purge_existing=True,
                db_url=mock_db_url)
    else:
        mc = catalog

    user = "test_format_basic"

    df1_spec = deepcopy(_df1_spec)
    df2_spec = deepcopy(_df2_spec)

    # success
    mc.add_format(df1_spec, user)

    # duplicate is bad
    with pytest.raises(DuplicateEntry):
        mc.add_format(df1_spec, user)

    # allow update of same version
    new_descr = 'a new description'
    df1_spec['self']['description'] = new_descr
    mc.add_format(df1_spec, user, update=True)

    # adding a new version is kosher
    new_ver = '2.0.0'
    df1_spec['self']['version'] = new_ver
    mc.add_format(df1_spec, user)

    # can't update a format that doesn't exist
    with pytest.raises(MissingEntry):
        mc.add_format(df2_spec, user, update=True)

    # get spec and make sure it's updated
    spec = mc.get_format_spec(df1_spec['self']['name'], version=None)
    assert spec['self']['version'] == new_ver
    assert spec['self']['description'] == new_descr


def test_discovery(mock_cli_config, mock_db_url, catalog=None):
    '''Tests creation of discovery objects'''
    if catalog is None:
        mc = MockCatalog(db_name='dcae_cli.test.db', purge_existing=True,
                enforce_image=False, db_url=mock_db_url)
    else:
        mc = catalog

    user = "test_discovery"

    c1_spec = deepcopy(_c1_spec)
    df1_spec = deepcopy(_df1_spec)
    c2_spec = deepcopy(_c2_spec)

    mc.add_format(df1_spec, user)
    mc.add_component(user, c1_spec)
    mc.add_component(user, c2_spec)

    params, interfaces = mc.get_discovery_for_docker(c1_spec['self']['name'], c1_spec['self']['version'])
    assert params == {'bar': 2, 'foo': 1}
    assert interfaces == {'call1': [('std.comp_two', '1.0.0')], 'pub1': [('std.comp_two', '1.0.0')]}


def _spec_tuple(dd):
    '''Returns a (name, version, component type) tuple from a given component spec dict'''
    return dd['self']['name'], dd['self']['version'], dd['self']['component_type']


def _comp_tuple_set(*dds):
    '''Runs a set of component spec tuples'''
    return set(map(_spec_tuple, dds))


def _format_tuple(dd):
    '''Returns a (name, version) tuple from a given data format spec dict'''
    return dd['self']['name'], dd['self']['version']


def _format_tuple_set(*dds):
    '''Runs a set of data format spec tuples'''
    return set(map(_format_tuple, dds))


def test_comp_list(mock_cli_config, mock_db_url, catalog=None):
    '''Tests the list functionality of the catalog'''
    if catalog is None:
        mc = MockCatalog(db_name='dcae_cli.test.db', purge_existing=True,
                enforce_image=False, db_url=mock_db_url)
    else:
        mc = catalog

    user = "test_comp_list"

    df1_spec = deepcopy(_df1_spec)
    df2_spec = deepcopy(_df2_spec)
    df2v2_spec = deepcopy(_df2v2_spec)

    c1_spec = deepcopy(_c1_spec)
    c2_spec = deepcopy(_c2_spec)
    c2v2_spec = deepcopy(_c2v2_spec)
    c3_spec = deepcopy(_c3_spec)

    mc.add_format(df1_spec, user)
    mc.add_format(df2_spec, user)
    mc.add_format(df2v2_spec, user)
    mc.add_component(user, c1_spec)
    mc.add_component(user, c2_spec)
    mc.add_component(user, c2v2_spec)
    mc.add_component(user, c3_spec)

    mc.add_component(user,_cdap_spec)

    def components_to_specs(components):
        return [ json.loads(c["spec"]) for c in components ]

    # latest by default. only v2 of c2
    components = mc.list_components()
    specs = components_to_specs(components)
    assert _comp_tuple_set(*specs) == _comp_tuple_set(c1_spec, c2v2_spec, c3_spec, _cdap_spec)

    # all components
    components = mc.list_components(latest=False)
    specs = components_to_specs(components)
    assert _comp_tuple_set(*specs) == _comp_tuple_set(c1_spec, c2_spec, c2v2_spec, c3_spec, _cdap_spec)

    components = mc.list_components(subscribes=[('std.format_one', None)])
    specs = components_to_specs(components)
    assert _comp_tuple_set(*specs) == _comp_tuple_set(c1_spec, c2v2_spec)

    # no comps subscribe to latest std.format_two
    components = mc.list_components(subscribes=[('std.format_two', None)])
    assert not components

    components = mc.list_components(subscribes=[('std.format_two', '1.5.0')])
    specs = components_to_specs(components)
    assert _comp_tuple_set(*specs) == _comp_tuple_set(c3_spec, _cdap_spec)

    # raise if format doesn't exist
    with pytest.raises(MissingEntry):
        mc.list_components(subscribes=[('std.format_two', '5.0.0')])

    components = mc.list_components(publishes=[('std.format_one', None)])
    specs = components_to_specs(components)
    assert _comp_tuple_set(*specs) == _comp_tuple_set(c1_spec, _cdap_spec)

    components = mc.list_components(calls=[(('std.format_one', None), ('std.format_one', None)), ])
    specs = components_to_specs(components)
    assert _comp_tuple_set(*specs) == _comp_tuple_set(c1_spec)

    # raise if format doesn't exist
    with pytest.raises(MissingEntry):
        mc.list_components(calls=[(('std.format_one', '5.0.0'), ('std.format_one', None)), ])

    components = mc.list_components(provides=[(('std.format_one', '1.0.0'), ('std.format_two', '1.5.0')), ])
    specs = components_to_specs(components)
    assert _comp_tuple_set(*specs) == _comp_tuple_set(c3_spec, _cdap_spec)

    # test for listing published components

    name_pub = c1_spec["self"]["name"]
    version_pub = c1_spec["self"]["version"]
    mc.publish_component(user, name_pub, version_pub)
    components = mc.list_components(only_published=True)
    specs = components_to_specs(components)
    assert _comp_tuple_set(*specs) == _comp_tuple_set(c1_spec)

    components = mc.list_components(only_published=False)
    assert len(components) == 4


def test_format_list(mock_cli_config, mock_db_url, catalog=None):
    '''Tests the list functionality of the catalog'''
    if catalog is None:
        mc = MockCatalog(db_name='dcae_cli.test.db', purge_existing=True,
                enforce_image=False, db_url=mock_db_url)
    else:
        mc = catalog

    user = "test_format_list"

    df1_spec = deepcopy(_df1_spec)
    df2_spec = deepcopy(_df2_spec)
    df2v2_spec = deepcopy(_df2v2_spec)

    mc.add_format(df1_spec, user)
    mc.add_format(df2_spec, user)
    mc.add_format(df2v2_spec, user)

    def formats_to_specs(components):
        return [ json.loads(c["spec"]) for c in components ]

    # latest by default. ensure only v2 of df2 makes it
    formats = mc.list_formats()
    specs = formats_to_specs(formats)
    assert _format_tuple_set(*specs) == _format_tuple_set(df1_spec, df2v2_spec)

    # list all
    formats = mc.list_formats(latest=False)
    specs = formats_to_specs(formats)
    assert _format_tuple_set(*specs) == _format_tuple_set(df1_spec, df2_spec, df2v2_spec)

    # test listing of published formats

    name_pub = df1_spec["self"]["name"]
    version_pub = df1_spec["self"]["version"]

    mc.publish_format(user, name_pub, version_pub)
    formats = mc.list_formats(only_published=True)
    specs = formats_to_specs(formats)
    assert _format_tuple_set(*specs) == _format_tuple_set(df1_spec)

    formats = mc.list_formats(only_published=False)
    assert len(formats) == 2


def test_component_add_cdap(mock_cli_config, mock_db_url, catalog=None):
    '''Adds a mock CDAP application'''
    if catalog is None:
        mc = MockCatalog(db_name='dcae_cli.test.db', purge_existing=True,
                db_url=mock_db_url)
    else:
        mc = catalog

    user = "test_component_add_cdap"

    df1_spec = deepcopy(_df1_spec)
    df2_spec = deepcopy(_df2_spec)

    mc.add_format(df1_spec, user)
    mc.add_format(df2_spec, user)

    mc.add_component(user, _cdap_spec)

    name, version, _ = _spec_tuple(_cdap_spec)
    jar_out, cdap_config_out, spec_out = mc.get_cdap(name, version)

    assert _cdap_spec["artifacts"][0]["uri"] == jar_out
    assert _cdap_spec["auxilary"] == cdap_config_out
    assert _cdap_spec == spec_out


def test_get_discovery_from_spec(mock_cli_config, mock_db_url):
    mc = MockCatalog(db_name='dcae_cli.test.db', purge_existing=True,
            enforce_image=False, db_url=mock_db_url)

    user = "test_get_discovery_from_spec"

    c1_spec_updated = deepcopy(_c1_spec)
    c1_spec_updated["streams"]["publishes"][0] = {
            'format': 'std.format_one',
            'version': '1.0.0',
            'config_key': 'pub1',
            'type': 'http'
            }
    c1_spec_updated["streams"]["subscribes"][0] = {
            'format': 'std.format_one',
            'version': '1.0.0',
            'route': '/sub1',
            'type': 'http'
            }

    # Case when c1 doesn't exist

    mc.add_format(_df1_spec, user)
    mc.add_component(user, _c2_spec)
    actual_params, actual_interface_map, actual_dmaap_config_keys \
            = mc.get_discovery_from_spec(user, c1_spec_updated, None)

    assert actual_params == {'bar': 2, 'foo': 1}
    assert actual_interface_map == { 'pub1': [('std.comp_two', '1.0.0')],
            'call1': [('std.comp_two', '1.0.0')] }
    assert actual_dmaap_config_keys == ([], [])

    # Case when c1 already exist

    mc.add_component(user,_c1_spec)

    c1_spec_updated["services"]["calls"][0]["config_key"] = "callme"
    actual_params, actual_interface_map, actual_dmaap_config_keys \
            = mc.get_discovery_from_spec(user, c1_spec_updated, None)

    assert actual_params == {'bar': 2, 'foo': 1}
    assert actual_interface_map == { 'pub1': [('std.comp_two', '1.0.0')],
            'callme': [('std.comp_two', '1.0.0')] }
    assert actual_dmaap_config_keys == ([], [])

    # Case where add in dmaap streams
    # TODO: Add in subscribes test case after spec gets pushed

    c1_spec_updated["streams"]["publishes"][0] = {
            'format': 'std.format_one',
            'version': '1.0.0',
            'config_key': 'pub1',
            'type': 'message router'
            }

    actual_params, actual_interface_map, actual_dmaap_config_keys \
            = mc.get_discovery_from_spec(user, c1_spec_updated, None)

    assert actual_params == {'bar': 2, 'foo': 1}
    assert actual_interface_map == { 'callme': [('std.comp_two', '1.0.0')] }
    assert actual_dmaap_config_keys == (["pub1"], [])

    # Case when cdap spec doesn't exist

    cdap_spec = deepcopy(_cdap_spec)
    cdap_spec["streams"]["publishes"][0] = {
            'format': 'std.format_one',
            'version': '1.0.0',
            'config_key': 'pub1',
            'type': 'http'
            }
    cdap_spec["streams"]["subscribes"][0] = {
            'format': 'std.format_two',
            'version': '1.5.0',
            'route': '/sub1',
            'type': 'http'
            }

    mc.add_format(_df2_spec, user)
    actual_params, actual_interface_map, actual_dmaap_config_keys \
            = mc.get_discovery_from_spec(user, cdap_spec, None)

    assert actual_params == {'program_preferences': [], 'app_config': {}, 'app_preferences': {}}
    assert actual_interface_map == {'pub1': [('std.comp_two', '1.0.0'), ('std.comp_one', '1.0.0')]}
    assert actual_dmaap_config_keys == ([], [])


def test_get_unpublished_formats(mock_cli_config, mock_db_url, catalog=None):
    if catalog is None:
        mc = MockCatalog(db_name='dcae_cli.test.db', purge_existing=True,
                enforce_image=False, db_url=mock_db_url)
    else:
        mc = catalog

    user = "test_get_unpublished_formats"

    mc.add_format(_df1_spec, user)
    mc.add_component(user, _c1_spec)

    # detect unpublished formats

    name_to_pub = _c1_spec["self"]["name"]
    version_to_pub = _c1_spec["self"]["version"]
    formats = mc.get_unpublished_formats(name_to_pub, version_to_pub)
    assert [('std.format_one', '1.0.0')] == formats

    # all formats published

    mc.publish_format(user, _df1_spec["self"]["name"], _df1_spec["self"]["version"])
    formats = mc.get_unpublished_formats(name_to_pub, version_to_pub)
    assert len(formats) == 0


def test_get_unique_format_things():
    def create_tuple(entry):
        return (entry["name"], entry["version"])

    def get_orm(name, version):
        return ("ORM", name, version)

    entries = [{"name": "abc", "version": 123},
            {"name": "abc", "version": 123},
            {"name": "abc", "version": 123},
            {"name": "def", "version": 456},
            {"name": "def", "version": 456}]

    get_unique_fake_format = partial(_get_unique_format_things, create_tuple,
            get_orm)
    expected = [("ORM", "abc", 123), ("ORM", "def", 456)]

    assert sorted(expected) == sorted(get_unique_fake_format(entries))


def test_filter_latest():
    orms = [('std.empty.get', '1.0.0'), ('std.unknown', '1.0.0'),
            ('std.unknown', '1.0.1'), ('std.empty.get', '1.0.1')]

    assert list(catalog._filter_latest(orms)) == [('std.empty.get', '1.0.1'), \
            ('std.unknown', '1.0.1')]


def test_raise_if_duplicate():
    class FakeOrig(object):
        args = ["unique", "duplicate"]

    url = "sqlite"
    orig = FakeOrig()
    error = IntegrityError("Error about uniqueness", None, orig)

    with pytest.raises(catalog.DuplicateEntry):
        catalog._raise_if_duplicate(url, error)

    # Couldn't find psycopg2.IntegrityError constructor nor way
    # to set pgcode so decided to mock it.
    class FakeOrigPostgres(object):
        pgcode = "23505"

    url = "postgres"
    orig = FakeOrigPostgres()
    error = IntegrityError("Error about uniqueness", None, orig)

    with pytest.raises(catalog.DuplicateEntry):
        catalog._raise_if_duplicate(url, error)


def test_get_docker_image_from_spec():
    assert "foo-image" == catalog._get_docker_image_from_spec(_c1_spec)

def test_get_cdap_jar_from_spec():
    assert "bahpomet.com" == catalog._get_cdap_jar_from_spec(_cdap_spec)


def test_build_config_keys_map():
    stub_spec = {
          'streams': {
              'publishes': [
                  {'format': 'std.format_one', 'version': '1.0.0',
                      'config_key': 'pub1', 'type': 'http'},
                  {'format': 'std.format_one', 'version': '1.0.0',
                      'config_key': 'pub2', 'type': 'message_router'}
                  ],
              'subscribes': [
                  {'format': 'std.format_one', 'version': '1.0.0', 'route': '/sub1',
                      'type': 'http'},
                  {'format': 'std.format_one', 'version': '1.0.0',
                      'config_key': 'sub2', 'type': 'message_router'}
                  ]
              },
          'services': {
              'calls': [
                  {'request': {'format': 'std.format_one', 'version': '1.0.0'},
                   'response': {'format': 'std.format_one', 'version': '1.0.0'},
                   'config_key': 'call1'}
                  ],
              'provides': [
                  {'request': {'format': 'std.format_one', 'version': '1.0.0'},
                   'response': {'format': 'std.format_one', 'version': '1.0.0'},
                   'route': '/prov1'}
                  ]
              }
          }

    grouping = catalog.build_config_keys_map(stub_spec)
    expected = {'call1': {'group': 'services_calls'}, 'pub1': {'type': 'http', 'group': 'streams_publishes'}, 'sub2': {'type': 'message_router', 'group': 'streams_subscribes'}, 'pub2': {'type': 'message_router', 'group': 'streams_publishes'}}
    assert expected == grouping


def test_get_data_router_subscriber_route():
    spec = {"streams": {"subscribes": [ { "type": "data_router", "config_key":
        "alpha", "route": "/alpha" }, { "type": "message_router", "config_key":
        "beta" } ]}}

    assert "/alpha" == catalog.get_data_router_subscriber_route(spec, "alpha")

    with pytest.raises(catalog.MissingEntry):
        catalog.get_data_router_subscriber_route(spec, "beta")

    with pytest.raises(catalog.MissingEntry):
        catalog.get_data_router_subscriber_route(spec, "gamma")


if __name__ == '__main__':
    '''Test area'''
    pytest.main([__file__, ])
