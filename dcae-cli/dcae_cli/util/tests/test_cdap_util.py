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

from dcae_cli.util.cdap_util import _merge_spec_config_into_broker_put,  normalize_cdap_params


def test_normalize_cdap_params():
    spec = {"parameters" : {}}
    normalized = normalize_cdap_params(spec)
    assert normalized == {"app_preferences" : {},
                         "app_config" : {},
                         "program_preferences" : []}

def test_cdap_util():
    """
    Tests both _merge_spec_config_into_broker_put and normalize_cdap_params
    """
    jar = "bahphomet.com/nexus/doomsday.jar"
    config = {
        "artifact_name" : "testname",
        "artifact_version" : "6.6.6",
        "streamname" : "stream",
        "programs" : [{"program_type" : "flows", "program_id" : "flow_id"}],
        "namespace" : "underworld"
    }
    spec = {
        "self": {
            "version": "6.6.6",
            "description": "description",
            "component_type": "cdap",
            "name": "name"
        },
        "parameters" : {
            "app_preferences" : [{"name" : "he", "description" : "", "value" :  "shall rise"}],
            "program_preferences" : [{"program_type" : "flows", "program_id" : "flow_id", "program_pref" : [{"name": "foo", "description" : "", "value" : "bar"}]}]
        },

        "streams": {
                      "publishes": [],
                      "subscribes" : []
                   },
        "services": {
                      "calls" : [],
                      'provides': [
                           {"request":   {"format" : 'std.format_one', "version" : "1.0.0"},
                            "response" : {"format" : "std.format_two", "version" : "1.5.0"},
                            "service_name" : "baphomet",
                            "service_endpoint" : "rises",
                            "verb" : "GET"}
                        ]
                    },
    }
    parsed_parameters = normalize_cdap_params(spec) 
    templated_conf = {"streams_publishes":{}, "streams_subscribes": {},
        "services_calls": {}} #TODO: Incorporate a test templated_conf
    broker_put = _merge_spec_config_into_broker_put(jar, config, spec, parsed_parameters, templated_conf)

    expected = {
        "app_config": {"services_calls" : {},
                       "streams_publishes" : {},
                       "streams_subscribes": {}
                      },
        "app_preferences": {"he" : "shall rise"},
        "artifact_name" : "testname",
        "artifact_version" : "6.6.6",
        "jar_url": "bahphomet.com/nexus/doomsday.jar",
        "namespace": "underworld",
        "program_preferences" : [{"program_type" : "flows", "program_id" : "flow_id", "program_pref" : {"foo" : "bar"}}],
        "programs" : [{"program_type" : "flows", "program_id" : "flow_id"}],
        "service_component_type": "cdap",
        "services": [{"service_name" : "baphomet", "service_endpoint" : "rises", "endpoint_method" : "GET"}],
        "streamname": "stream",
        "cdap_application_type" : "program-flowlet"
        }

    assert broker_put == expected
