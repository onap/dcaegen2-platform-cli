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
import pytest
import json, copy

from dcae_cli.catalog.mock.schema import validate_component, validate_format,apply_defaults_docker_config, apply_defaults
from dcae_cli.catalog.mock import schema
from dcae_cli.util.exc import DcaeException


format_test = r'''
{
  "self": {
    "name": "asimov.format.integerClassification",
    "version": "1.0.0",
    "description": "Represents a single classification from a machine learning model - just a test version"
  },
  "dataformatversion": "1.0.0",
  "jsonschema": {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "type": "object",
      "properties": {
          "classification": {
              "type": "string"
          }
      },
      "additionalProperties": false
   }
}
'''


component_test = r'''
{
  "self": {
    "version": "1.0.0",
    "name": "asimov.component.kpi_anomaly",
    "description": "Classifies VNF KPI data as anomalous",
    "component_type": "docker"
  },
  "streams": {
    "subscribes": [
      {
        "format": "dcae.vnf.kpi",
        "version": "1.0.0",
        "route": "/data",
        "type": "http"
      },
      {
        "format":"std.format_one",
        "version":"1.0.0",
        "config_key":"sub2",
        "type": "message router"
      }
    ],
    "publishes": [
      {
        "format": "asimov.format.integerClassification",
        "version": "1.0.0",
        "config_key": "prediction",
        "type": "http"
      },
      {
        "format":"std.format_one",
        "version":"1.0.0",
        "config_key":"pub2",
        "type": "message router"
      }
    ]
  },
  "services": {
    "calls": [],
    "provides": [
      {
        "route": "/score-vnf",
        "request": {
          "format": "dcae.vnf.kpi",
          "version": "1.0.0"
        },
        "response": {
          "format": "asimov.format.integerClassification",
          "version": "1.0.0"
        }
      }
    ]
  },
  "parameters": [
    {
      "name": "threshold",
      "value": 0.75,
      "description": "Probability threshold to exceed to be anomalous",
      "designer_editable": false,
      "sourced_at_deployment": false,
      "policy_editable": false
    }
  ],
  "artifacts": [
    {
      "uri": "somedockercontainerpath",
      "type": "docker image"
    }
    ],
  "auxilary": {
    "healthcheck": {
      "type": "http",
      "endpoint": "/health"
    }
  }
}
'''

cdap_component_test = r'''
{  
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
         },
         {  
            "format":"std.format_one",
            "version":"1.0.0",
            "config_key":"pub2",
            "type": "message router"
         }
      ],
      "subscribes":[  
         {  
            "format":"std.format_two",
            "version":"1.5.0",
            "route":"/sub1",
            "type": "http"
         },
         {  
            "format":"std.format_one",
            "version":"1.0.0",
            "config_key":"sub2",
            "type": "message router"
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
   "parameters":[  

   ],
   "artifacts": [
     {
       "uri": "somecdapjarurl",
       "type": "jar"
     }
     ],
   "auxilary": {
     "streamname":"who",
     "artifact_name" : "HelloWorld",
     "artifact_version" : "3.4.3",
     "programs" : [
                    {"program_type" : "flows", "program_id" : "WhoFlow"},
                    {"program_type" : "services", "program_id" : "Greeting"}
                  ],
     "namespace" : "hw"
   }
}
'''


def test_basic(mock_cli_config):
    validate_component(json.loads(component_test))
    validate_format(json.loads(format_test))
    validate_component(json.loads(cdap_component_test))

    # Test with DR publishes for cdap
    dr_publishes = { "format":"std.format_one", "version":"1.0.0",
            "config_key":"pub3", "type": "data router" }
    cdap_valid = json.loads(cdap_component_test)
    cdap_valid["streams"]["publishes"].append(dr_publishes)

    # Test with DR subscribes for cdap
    cdap_invalid = json.loads(cdap_component_test)
    ss = cdap_invalid["streams"]["subscribes"][0]
    ss["type"] = "data_router"
    ss["config_key"] = "nada"
    cdap_invalid["streams"]["subscribes"][0] = ss

    with pytest.raises(DcaeException):
        validate_component(cdap_invalid)



def test_validate_docker_config(mock_cli_config):

    def compose_spec(config):
        spec = json.loads(component_test)
        spec["auxilary"] = config
        return spec

    good_docker_configs = [
            {
                "healthcheck": {
                    "type": "http",
                    "endpoint": "/health",
                    "interval": "15s",
                    "timeout": "1s"
                }
            },
            {
                "healthcheck": {
                    "type": "script",
                    "script": "curl something"
                    }
            }]

    for good_config in good_docker_configs:
        spec = compose_spec(good_config)
        assert validate_component(spec) == None

    bad_docker_configs = [
            #{},
            {
                "healthcheck": {}
            },
            {
                "healthcheck": {
                    "type": "http"
                }
            },
            {
                "healthcheck": {
                    "type": "http",
                    "script": "huh"
                }
            }]

    for bad_config in bad_docker_configs:
        with pytest.raises(DcaeException):
            spec = compose_spec(bad_config)
            validate_component(spec)


def test_validate_cdap_config(mock_cli_config):

    def compose_spec(config):
        spec = json.loads(cdap_component_test)
        spec["auxilary"] = config
        return spec

    good_cdap_configs = [
       {
           "streamname":"streamname",
           "artifact_version":"6.6.6",
           "artifact_name" : "testname",
           "programs" : [],
       },
       {
           "streamname":"streamname",
           "artifact_version":"6.6.6",
           "artifact_name" : "testname",
           "programs" : [{"program_type" : "flows", "program_id" : "flow_id"}],
           "program_preferences" : [{"program_type" : "flows", "program_id" : "flow_id", "program_pref" : {"he" : "shall rise"}}],
           "namespace" : "this should be an optional field",
           "app_preferences" : {"he" : "shall rise"}
       }
    ]

    for good_config in good_cdap_configs:
        spec = compose_spec(good_config)
        assert validate_component(spec) == None

    bad_cdap_configs = [
            {},
            {"YOU HAVE" : "ALWAYS FAILED ME"}
            ]

    for bad_config in bad_cdap_configs:
        with pytest.raises(DcaeException):
            spec = compose_spec(bad_config)
            validate_component(bad_config)


def test_apply_defaults():
    definition = { "length": { "default": 10 }, "duration": { "default": "10s" } }

    # Test: Add expected properties
    properties = {}
    actual = apply_defaults(definition, properties)
    assert actual == { "length": 10, "duration": "10s" }

    # Test: Don't mess with existing values
    properties = { "length": 100, "duration": "100s" }
    actual = apply_defaults(definition, properties)
    assert actual == properties

    # Test: No defaults to apply
    definition = { "length": {}, "duration": {} }
    properties = { "width": 100 }
    actual = apply_defaults(definition, properties)
    assert actual == properties

    # Test: Nested object
    definition = { "length": { "default": 10 }, "duration": { "default": "10s" },
            "location": { "properties": { "lat": { "default": "40" },
                "long": { "default": "75" }, "alt": {} } } }
    actual = apply_defaults(definition, {})
    assert actual == {'duration': '10s', 'length': 10,
            'location': {'lat': '40', 'long': '75'}}


def test_apply_defaults_docker_config(mock_cli_config):
    # Test: Adding of missing expected properties for http
    dc = { "healthcheck": { "type": "http", "endpoint": "/foo" } }
    actual = apply_defaults_docker_config(dc)

    assert "interval" in actual["healthcheck"]
    assert "timeout" in actual["healthcheck"]

    # Test: Adding of missing expected properties for script
    dc = { "healthcheck": { "type": "script", "script": "/bin/do-something" } }
    actual = apply_defaults_docker_config(dc)

    assert "interval" in actual["healthcheck"]
    assert "timeout" in actual["healthcheck"]

    # Test: Expected properties already exist
    dc = { "healthcheck": { "type": "http", "endpoint": "/foo",
        "interval": "10000s", "timeout": "100000s" } }
    actual = apply_defaults_docker_config(dc)
    assert dc == actual

    # Test: Never should happen
    dc = { "healthcheck": { "type": "bogus" } }
    actual = apply_defaults_docker_config(dc)
    assert dc == actual


def test_validate():
    fake_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "Test schema",
            "type": "object",
            "properties": {
                "foo": { "type": "string" },
                "bar": { "type": "integer" }
                },
            "required": ["foo", "bar"]
            }

    good_path = "/correct_path"

    def fetch_schema(path):
        if path == good_path:
            return fake_schema
        else:
            raise schema.FetchSchemaError("Schema not found")

    # Success case

    good_instance = { "foo": "hello", "bar": 1776 }

    schema._validate(fetch_schema, good_path, good_instance)

    # Error from validating

    bad_instance = {}

    with pytest.raises(DcaeException):
        schema._validate(fetch_schema, good_path, bad_instance)

    # Error from fetching

    bad_path = "/wrong_path"

    with pytest.raises(DcaeException):
        schema._validate(fetch_schema, bad_path, good_instance)
