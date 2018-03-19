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
Provides tests for the discovery module
'''
import json
from functools import partial
from copy import deepcopy

import pytest

from dcae_cli.util import discovery as dis
from dcae_cli.util.discovery import create_config, Consul, config_context, DiscoveryNoDownstreamComponentError


user = 'bob'
cname = 'asimov.test_comp'
cver = '0.0.0'
inst_pref = 'abc123'
params = {'param0': 12345}


def test_create_config():
    '''
    Test explanation:
    1. param1 in the component spec has 2 compatible component types, comp1 and comp2. however infrastructure
    support only allows for 1. thus comp2 shouldn't make it to the rels.
    2. comp1 has two instances, so both should make it to the rels
    3. param2 is compatible with comp3, but there are no comp3 instances. thus it's missing from rels.
    '''
    expected_ckey = 'bob.abc123.0-0-0.asimov-test_comp'
    expected_conf = {'param1': '{{1-1-1.foo-bar-comp1}}', 'param0': 12345, 'param2': '{{3-3-3.foo-bar-comp3}}'}
    expected_rkey = 'bob.abc123.0-0-0.asimov-test_comp:rel'
    expected_rels = ['bob.aaa111.1-1-1.foo-bar-comp1.suffix',
            'bob.bbb222.1-1-1.foo-bar-comp1.suffix',
            'bob.ddd444.3-3-3.foo-bar-comp3.suffix']
    expected_dmaap_key = 'bob.abc123.0-0-0.asimov-test_comp:dmaap'
    expected_dmaap_map = {}

    interface_map = {'param1': [('foo.bar.comp1', '1.1.1'),
                                ('foo.bar.comp2', '2.2.2')],
                     'param2': [('foo.bar.comp3', '3.3.3')]
                     }
    instance_map = {('foo.bar.comp1', '1.1.1'): ['bob.aaa111.1-1-1.foo-bar-comp1.suffix',
                                                 'bob.bbb222.1-1-1.foo-bar-comp1.suffix'],
                    ('foo.bar.comp2', '2.2.2'): ['bob.ccc333.2-2-2.foo-bar-comp2.suffix'],
                    ('foo.bar.comp3', '3.3.3'): ['bob.ddd444.3-3-3.foo-bar-comp3.suffix']}

    ckey, conf, rkey, rels, dmaap_key, dmaap_map  = create_config(user, cname, cver,
            params, interface_map, instance_map, expected_dmaap_map, inst_pref)

    assert ckey == expected_ckey
    assert conf == expected_conf
    assert rkey == expected_rkey
    assert sorted(rels) == sorted(expected_rels)
    assert dmaap_key == expected_dmaap_key
    assert dmaap_map == expected_dmaap_map

    #
    # Fail cases: When a downstream dependency does not exist
    #

    # (1) Case when there's no actual instance
    instance_map_missing_3 = deepcopy(instance_map)
    instance_map_missing_3[('foo.bar.comp3', '3.3.3')] = []

    with pytest.raises(DiscoveryNoDownstreamComponentError):
        create_config(user, cname, cver, params, interface_map, instance_map_missing_3,
                expected_dmaap_map, inst_pref)

    # (2) Case when there's no existence in instance_map
    interface_map_extra = deepcopy(interface_map)
    interface_map_extra["param_not_exist"] = []

    with pytest.raises(DiscoveryNoDownstreamComponentError):
        create_config(user, cname, cver, params, interface_map_extra, instance_map,
                expected_dmaap_map, inst_pref)

    #
    # Force the fail cases to succeed
    #

    # (1)
    ckey, conf, rkey, rels, dmaap_key, dmaap_map = create_config(user, cname, cver,
            params, interface_map, instance_map_missing_3, expected_dmaap_map, inst_pref,
            force=True)

    assert ckey == expected_ckey
    assert conf == expected_conf
    assert rkey == expected_rkey
    # Remove the foo.bar.comp3:3.3.3 instance because we are simulating when that
    # instance does not exist
    assert sorted(rels) == sorted(expected_rels[:2])
    assert dmaap_key == expected_dmaap_key
    assert dmaap_map == expected_dmaap_map

    # (2)
    ckey, conf, rkey, rels, dmaap_key, dmaap_map = create_config(user, cname, cver,
            params, interface_map_extra, instance_map, expected_dmaap_map, inst_pref,
            force=True)

    expected_conf["param_not_exist"] = "{{}}"

    assert ckey == expected_ckey
    assert conf == expected_conf
    assert rkey == expected_rkey
    assert sorted(rels) == sorted(expected_rels)
    assert dmaap_key == expected_dmaap_key
    assert dmaap_map == expected_dmaap_map

    #
    # Test differnt dashes scenario
    #

    # Component has been added with dashes but the instance comes back with dots
    # because the discovery layer always brings back instances with dots
    interface_map_dashes = {'param1': [('foo-bar-comp1', '1.1.1')]}
    instance_map_dashes = {('foo.bar.comp1', '1.1.1'):
            ['bob.aaa111.1-1-1.foo-bar-comp1.suffix']}

    with pytest.raises(DiscoveryNoDownstreamComponentError):
        create_config(user, cname, cver, params, interface_map_dashes, instance_map_dashes,
                expected_dmaap_map, inst_pref)

    # The fix in v2.3.2 was to have the caller to send in instances with dots and
    # with dashes
    instance_map_dashes = {
            ('foo.bar.comp1', '1.1.1'): ['bob.aaa111.1-1-1.foo-bar-comp1.suffix'],
            ('foo-bar-comp1', '1.1.1'): ['bob.aaa111.1-1-1.foo-bar-comp1.suffix'] }

    ckey, conf, rkey, rels, dmaap_key, dmaap_map = create_config(user, cname, cver,
            params, interface_map_dashes, instance_map_dashes, expected_dmaap_map, inst_pref)

    # The expecteds have changed because the inputs have been narrowed to just
    # one
    assert ckey == expected_ckey
    assert conf == {'param1': '{{1-1-1.foo-bar-comp1}}', 'param0': 12345}
    assert rkey == expected_rkey
    assert sorted(rels) == sorted(['bob.aaa111.1-1-1.foo-bar-comp1.suffix'])
    assert dmaap_key == expected_dmaap_key
    assert dmaap_map == expected_dmaap_map

    # Pass in a non-empty dmaap map
    dmaap_map_input = { "some-config-key": { "type": "message_router",
        "dmaap_info": {"topic_url": "http://some-topic-url.com/abc"} } }
    del expected_conf["param_not_exist"]
    expected_conf["some-config-key"] = { "type": "message_router",
            "dmaap_info": "<<some-config-key>>" }

    ckey, conf, rkey, rels, dmaap_key, dmaap_map  = create_config(user, cname, cver,
            params, interface_map, instance_map, dmaap_map_input, inst_pref)

    assert ckey == expected_ckey
    assert conf == expected_conf
    assert rkey == expected_rkey
    assert sorted(rels) == sorted(expected_rels)
    assert dmaap_key == expected_dmaap_key
    assert dmaap_map == {'some-config-key': {'topic_url': 'http://some-topic-url.com/abc'}}


@pytest.mark.skip(reason="Not a pure unit test")
def test_config_context(mock_cli_config):
    interface_map = {'param1': [('foo.bar.comp1', '1.1.1'),
                                ('foo.bar.comp2', '2.2.2')],
                     'param2': [('foo.bar.comp3', '3.3.3')]
                     }
    instance_map = {('foo.bar.comp1', '1.1.1'): ['bob.aaa111.1-1-1.foo-bar-comp1.suffix',
                                                 'bob.bbb222.1-1-1.foo-bar-comp1.suffix'],
                    ('foo.bar.comp2', '2.2.2'): ['bob.ccc333.2-2-2.foo-bar-comp2.suffix'],
                    ('foo.bar.comp3', '3.3.3'): ['bob.ddd444.3-3-3.foo-bar-comp3.suffix']}

    config_key_map = {"param1": {"group": "streams_publishes", "type": "http"},
            "param2": {"group": "services_calls", "type": "http"}}

    ckey = 'bob.abc123.0-0-0.asimov-test_comp'
    rkey = 'bob.abc123.0-0-0.asimov-test_comp:rel'
    expected_conf = {"streams_publishes": {'param1': '{{1-1-1.foo-bar-comp1}}'},
            'param0': 12345, "streams_subscribes": {},
            "services_calls": {'param2': '{{3-3-3.foo-bar-comp3}}'}}
    expected_rels = ['bob.aaa111.1-1-1.foo-bar-comp1.suffix',
            'bob.bbb222.1-1-1.foo-bar-comp1.suffix',
            'bob.ddd444.3-3-3.foo-bar-comp3.suffix']

    c = Consul(dis.default_consul_host())
    with config_context(user, cname, cver, params, interface_map, instance_map,
            config_key_map, instance_prefix=inst_pref) as (instance,_):
        assert json.loads(c.kv.get(ckey)[1]['Value'].decode('utf-8')) == expected_conf
        assert sorted(json.loads(c.kv.get(rkey)[1]['Value'].decode('utf-8'))) \
                == sorted(expected_rels)
        assert instance == ckey

    assert c.kv.get(ckey)[1] is None
    assert c.kv.get(rkey)[1] is None

    # Fail case: When a downstream dependency does not exist
    interface_map_extra = deepcopy(interface_map)
    interface_map_extra["param_not_exist"] = []

    with pytest.raises(DiscoveryNoDownstreamComponentError):
        with config_context(user, cname, cver, params, interface_map_extra,
                instance_map, config_key_map, instance_prefix=inst_pref) as (instance,_):
            pass

    # Force fail case to succeed
    expected_conf["param_not_exist"] = "{{}}"

    with config_context(user, cname, cver, params, interface_map_extra,
            instance_map, config_key_map, instance_prefix=inst_pref,
            force_config=True) as (instance,_):
        assert json.loads(c.kv.get(ckey)[1]['Value'].decode('utf-8')) == expected_conf
        assert sorted(json.loads(c.kv.get(rkey)[1]['Value'].decode('utf-8'))) \
            == sorted(expected_rels)
        assert instance == ckey


def test_inst_regex():
    ckey = 'bob.abc123.0-0-0.asimov-test_comp'
    match = dis._inst_re.match(ckey)
    assert match != None

    # Big version case

    ckey = 'bob.abc123.100-100-100.asimov-test_comp'
    match = dis._inst_re.match(ckey)
    assert match != None


def test_is_healthy_pure():
    component = { 'CreateIndex': 204546, 'Flags': 0,
            'Key': 'mike.21fbcabd-fac1-4b9b-9d18-2f624bfa44a5.0-4-0.sandbox-platform-dummy_subscriber', 'LockIndex': 0, 'ModifyIndex': 204546,
            'Value': b'{}' }

    component_health_good = ('262892',
            [{'Checks': [{'CheckID': 'serfHealth',
                   'CreateIndex': 3,
                   'ModifyIndex': 3,
                   'Name': 'Serf Health Status',
                   'Node': 'agent-one',
                   'Notes': '',
                   'Output': 'Agent alive and reachable',
                   'ServiceID': '',
                   'ServiceName': '',
                   'Status': 'passing'},
                  {'CheckID': 'service:rework-central-swarm-master:mike.21fbcabd-fac1-4b9b-9d18-2f624bfa44a5.0-4-0.sandbox-platform-dummy_subscriber:8080',
                   'CreateIndex': 204550,
                   'ModifyIndex': 204551,
                   'Name': 'Service '
                           "'mike.21fbcabd-fac1-4b9b-9d18-2f624bfa44a5.0-4-0.sandbox-platform-dummy_subscriber' "
                           'check',
                   'Node': 'agent-one',
                   'Notes': '',
                   'Output': '',
                   'ServiceID': 'rework-central-swarm-master:mike.21fbcabd-fac1-4b9b-9d18-2f624bfa44a5.0-4-0.sandbox-platform-dummy_subscriber:8080',
                   'ServiceName': 'mike.21fbcabd-fac1-4b9b-9d18-2f624bfa44a5.0-4-0.sandbox-platform-dummy_subscriber',
                   'Status': 'passing'}],
       'Node': {'Address': '10.170.2.17',
                'CreateIndex': 3,
                'ModifyIndex': 262877,
                'Node': 'agent-one',
                'TaggedAddresses': {'wan': '10.170.2.17'}},
       'Service': {'Address': '196.207.170.175',
                   'CreateIndex': 204550,
                   'EnableTagOverride': False,
                   'ID': 'rework-central-swarm-master:mike.21fbcabd-fac1-4b9b-9d18-2f624bfa44a5.0-4-0.sandbox-platform-dummy_subscriber:8080',
                   'ModifyIndex': 204551,
                   'Port': 33064,
                   'Service': 'mike.21fbcabd-fac1-4b9b-9d18-2f624bfa44a5.0-4-0.sandbox-platform-dummy_subscriber',
                   'Tags': None}}])

    assert True == dis._is_healthy_pure(lambda name: component_health_good, component)

    # Case: Check is failing

    component_health_bad = deepcopy(component_health_good)
    # NOTE: The failed status here. Not sure if this is what Consul actually sends
    # but at least its not "passing"
    component_health_bad[1][0]["Checks"][0]["Status"] = "failing"

    assert False == dis._is_healthy_pure(lambda name: component_health_bad, component)

    # Case: No health for a component

    component_health_nothing = ('262892', [])
    assert False == dis._is_healthy_pure(lambda name: component_health_nothing, component)


def test_get_instances_from_kv():

    def get_from_kv_fake(result, user, recurse=True):
        return "don't care about first arg", result

    user = "jane"
    kvs_nothing = []

    assert dis._get_instances_from_kv(partial(get_from_kv_fake, kvs_nothing), user) == []

    kvs_success = [ { "Value": "some value", "Key": "jane.1344a03a-06a8-4b92-bfac-d8f89df0c0cd.1-0-0.dcae-controller-ves-collector:rel"
        },
        { "Value": "some value", "Key": "jane.1344a03a-06a8-4b92-bfac-d8f89df0c0cd.1-0-0.dcae-controller-ves-collector" } ]

    assert dis._get_instances_from_kv(partial(get_from_kv_fake, kvs_success), user) == ["jane.1344a03a-06a8-4b92-bfac-d8f89df0c0cd.1-0-0.dcae-controller-ves-collector"]

    kvs_partial = [ { "Value": "some value", "Key": "jane.1344a03a-06a8-4b92-bfac-d8f89df0c0cd.1-0-0.dcae-controller-ves-collector:rel"
        } ]

    assert dis._get_instances_from_kv(partial(get_from_kv_fake, kvs_partial), user) == ["jane.1344a03a-06a8-4b92-bfac-d8f89df0c0cd.1-0-0.dcae-controller-ves-collector"]


def test_get_instances_from_catalog():

    def get_from_catalog_fake(result):
        return ("some Consul index", result)

    user = "jane"
    services_nothing = {}

    assert dis._get_instances_from_catalog(
            partial(get_from_catalog_fake, services_nothing), user) == []

    services_no_matching = { '4f09bb72-8578-4e82-a6a4-9b7d679bd711.cdap_app_hello_world.hello-world-cloudify-test': [],
  '666.fake_testing_service.rework-central.com': [],
  'Platform_Dockerhost_Solutioning_Test': [],
  'jack.2271ec6b-9224-4f42-b0b0-bfa91b41218f.1-0-1.cdap-event-proc-map-app': [],
  'jack.bca28c8c-a352-41f1-81bc-63ff46db2582.1-0-1.cdap-event-proc-supplement-app':
  [] }

    assert dis._get_instances_from_catalog(
            partial(get_from_catalog_fake, services_no_matching), user) == []

    services_success = { '4f09bb72-8578-4e82-a6a4-9b7d679bd711.cdap_app_hello_world.hello-world-cloudify-test': [],
  '666.fake_testing_service.rework-central.com': [],
  'Platform_Dockerhost_Solutioning_Test': [],
  'jack.2271ec6b-9224-4f42-b0b0-bfa91b41218f.1-0-1.cdap-event-proc-map-app': [],
  'jane.bca28c8c-a352-41f1-81bc-63ff46db2582.1-0-1.cdap-event-proc-supplement-app':
  [] }

    assert dis._get_instances_from_catalog(
            partial(get_from_catalog_fake, services_success), user) == ['jane.bca28c8c-a352-41f1-81bc-63ff46db2582.1-0-1.cdap-event-proc-supplement-app']


def test_merge_instances():
    user = "somebody"
    group_one = [ "123", "456" ]
    group_two = [ "123", "abc" ]
    group_three = []

    assert sorted(dis._merge_instances(user, lambda user: group_one, lambda user: group_two,
            lambda user: group_three)) == sorted([ "123", "456", "abc" ])


def test_make_instance_map():
    instances_latest_format = ["mike.112e4faa-2ac8-4b13-93e9-8924150538d5.0-5-0.sandbox-platform-laika"]

    instances_map = dis._make_instances_map(instances_latest_format)
    assert instances_map.get(("sandbox.platform.laika", "0.5.0")) == set(instances_latest_format)


def test_get_component_instances(monkeypatch):
    instances = [
            'jane.b493b48b-5fdf-4c1d-bd2a-8ce747b918ba.1-0-0.dcae-controller-ves-collector',
            'jane.2455ec5c-67e6-4d4d-8581-79037c7b5f8e.1-0-0.dcae-controller-ves-collector.rework-central.dcae.com',
            'jane.bfbb1356-d703-4007-8799-759a9e1fc8c2.1-0-0.dcae-controller-ves-collector.rework-central.dcae.com',
            'jane.89d82ff6-1482-4c01-8758-db9325aad085.1-0-0.dcae-controller-ves-collector'
            ]

    instances_map =  { ('dcae.controller.ves.collector', '1.0.0'): set(instances) }

    def get_user_instances_mock(user, consul_host=None, filter_instances_func=None):
        return instances_map

    monkeypatch.setattr(dis, 'get_user_instances', get_user_instances_mock)

    def always_true_filter(consul_host, instance):
        return True

    # Test base case

    user = "jane"
    cname = "dcae.controller.ves.collector"
    cver = "1.0.0"
    consul_host = "bogus"

    assert sorted(dis._get_component_instances(always_true_filter, user, cname, cver,
        consul_host)) == sorted(instances)

    # Test for dashes

    cname = "dcae-controller-ves-collector"

    assert sorted(dis._get_component_instances(always_true_filter, user, cname, cver,
        consul_host)) == sorted(instances)


def test_group_config():
    config_key_map = {'call1': {'group': 'services_calls'}, 'pub1': {'type': 'http', 'group': 'streams_publishes'}, 'sub2': {'type': 'message_router', 'group': 'streams_subscribes'}, 'pub2': {'type': 'message_router', 'group': 'streams_publishes'}}

    config = { "call1": "{{yo}}", "pub1": "{{target}}", "some-param": 123,
            "sub2": { "dmaap_info": "<<sub2>>" }, "pub2": { "dmaap_info": "<<pub2>>" } }

    gc = dis._group_config(config, config_key_map)
    expected = {'services_calls': {'call1': '{{yo}}'}, 'streams_publishes': {'pub2': {'dmaap_info': '<<pub2>>'}, 'pub1': '{{target}}'}, 'some-param': 123, 'streams_subscribes': {'sub2': {'dmaap_info': '<<sub2>>'}}}

    assert gc == expected


def test_parse_instance_lookup():
    results = [{"ServiceAddress": "192.168.1.100", "ServicePort": "8080"},
            {"ServiceAddress": "10.100.1.100", "ServicePort": "8081"}]
    assert dis.parse_instance_lookup(results) == "192.168.1.100:8080"


def test_apply_inputs():
    updated_config = dis._apply_inputs({"foo": "bar"}, {"foo": "baz"})
    assert updated_config == {"foo": "baz"}


def test_choose_consul_host(monkeypatch):
    def fake_default_consul_host():
        return "default-consul-host"

    monkeypatch.setattr(dis, "default_consul_host", fake_default_consul_host)
    assert "default-consul-host" == dis._choose_consul_host(None)
    assert "provided-consul-host" == dis._choose_consul_host("provided-consul-host")


if __name__ == '__main__':
    '''Test area'''
    pytest.main([__file__, ])
