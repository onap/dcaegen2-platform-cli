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
Tests for dmaap module
"""
import pytest
from dcae_cli.util import dmaap
from dcae_cli.util.exc import DcaeException


def test_validate_dmaap_map_schema_message_router():
    def pack_her_up(entry):
        return { "some-config-key": entry }

    good = {
        "type": "message_router",
        "aaf_username": "foo3",
        "aaf_password": "bar3",
        "dmaap_info": {
           "client_role":"com.dcae.member",
           "client_id":"1500462518108",
           "location":"mtc5",
            "topic_url":"https://dcae-msrt-ftl2.com:3905/events/com.dcae.dmaap.FTL2.TommyTestTopic2"
            }
        }
    dmaap.validate_dmaap_map_schema(pack_her_up(good))

    good_minimal = {
            "type": "message_router",
            "dmaap_info": {
                "topic_url":"https://dcae-msrt-ftl2.com:3905/events/com.dcae.dmaap.FTL2.TommyTestTopic2"
                }
            }
    dmaap.validate_dmaap_map_schema(pack_her_up(good_minimal))

    bad_extra = {
        "type": "message_router",
        "aaf_username": "foo3",
        "aaf_password": "bar3",
        "something_else": "boo",
        "dmaap_info": {
           "client_role":"com.dcae.member",
           "client_id":"1500462518108",
           "location":"mtc5",
           "topic_url":"https://dcae-msrt-ftl2.com:3905/events/com.dcae.dmaap.FTL2.TommyTestTopic2"
           }
        }
    dm = { "some-config-key": bad_extra }


    with pytest.raises(DcaeException):
        dmaap.validate_dmaap_map_schema(dm)

    bad_missing = {
        "type": "message_router",
        "aaf_username": "foo3",
        "aaf_password": "bar3",
        "dmaap_info": {
           "client_role":"com.dcae.member",
           "client_id":"1500462518108",
           "location":"mtc5"
           }
        }
    dm = { "some-config-key": bad_missing }

    with pytest.raises(DcaeException):
        dmaap.validate_dmaap_map_schema(dm)


def test_validate_dmaap_map_schema_data_router():
    def pack_her_up(entry):
        return { "some-config-key": entry }

    # Publishers
    good = {
        "type": "data_router",
        "dmaap_info": {
            "location": "mtc5",
            "publish_url": "http://some-publish-url/123",
            "log_url": "http://some-log-url/456",
            "username": "jane",
            "password": "abc"
            }
        }
    dmaap.validate_dmaap_map_schema(pack_her_up(good))

    good_minimal = {
            "type": "data_router",
            "dmaap_info": {
                "publish_url": "http://some-publish-url/123"
                }
            }
    dmaap.validate_dmaap_map_schema(pack_her_up(good_minimal))

    bad_extra = {
            "type": "data_router",
            "dmaap_info": {
                "publish_url": "http://some-publish-url/123",
                "unknown_key": "value"
                }
            }
    with pytest.raises(DcaeException):
        dmaap.validate_dmaap_map_schema(pack_her_up(bad_extra))

    # Subscribers
    good = {
        "type": "data_router",
        "dmaap_info": {
            "username": "drdeliver",
            "password": "1loveDataR0uter",
            "location": "loc00",
            "delivery_url": "https://example.com/whatever",
            "subscriber_id": "1550"
            }
        }
    dmaap.validate_dmaap_map_schema(pack_her_up(good))

    good_minimal = {
            "type": "data_router",
            "dmaap_info": {
                "delivery_url": "https://example.com/whatever"
                }
            }
    dmaap.validate_dmaap_map_schema(pack_her_up(good_minimal))

    bad_extra = {
            "type": "data_router",
            "dmaap_info": {
                "delivery_url": "https://example.com/whatever",
                "unknown_key": "value"
                }
            }
    with pytest.raises(DcaeException):
        dmaap.validate_dmaap_map_schema(pack_her_up(bad_extra))


def test_validate_dmaap_map_entries():

    # Success

    dmaap_map = { "mr_pub_fun": { "foo": "bar" }, "mr_sub_fun": { "baz": "duh"} }
    mr_config_keys = [ "mr_pub_fun", "mr_sub_fun" ]
    dr_config_keys = []

    assert dmaap.validate_dmaap_map_entries(dmaap_map, mr_config_keys, dr_config_keys) == True

    # Not supposed to be empty

    dmaap_map = {}

    assert dmaap.validate_dmaap_map_entries(dmaap_map, mr_config_keys, dr_config_keys) == False

    # Too many in dmaap map

    # NOTE: This scenario has been changed to be a success case per Tommy who
    # believes that having extra keys in the dmaap_map is harmless. People would
    # want to have a master dmaap_map that has a superset of connections used
    # across many components.

    dmaap_map = { "mr_pub_fun": { "foo": "bar" }, "mr_sub_fun": { "baz": "duh"} }
    mr_config_keys = [ "mr_pub_fun" ]
    dr_config_keys = []

    assert dmaap.validate_dmaap_map_entries(dmaap_map, mr_config_keys, dr_config_keys) == True

    # Too little in dmaap map

    dmaap_map = { "mr_pub_fun": { "foo": "bar" }, "mr_sub_fun": { "baz": "duh"} }
    mr_config_keys = [ "mr_pub_fun", "mr_sub_fun", "mr_xxx" ]
    dr_config_keys = []

    assert dmaap.validate_dmaap_map_entries(dmaap_map, mr_config_keys, dr_config_keys) == False


def test_apply_defaults_dmaap_map():
    good = {
        "type": "message_router",
        "aaf_username": "foo3",
        "aaf_password": "bar3",
        "dmaap_info": {
           "client_role":"com.dcae.member",
           "client_id":"1500462518108",
           "location":"mtc5",
            "topic_url":"https://dcae-msrt-ftl2.com:3905/events/com.dcae.dmaap.FTL2.TommyTestTopic2"
            }
        }
    dm = { "some-config-key": good }

    assert dmaap.apply_defaults_dmaap_map(dm) == dm

    minimal = {
        "type": "message_router",
        "dmaap_info": {
            "topic_url":"https://dcae-msrt-ftl2.com:3905/events/com.dcae.dmaap.FTL2.TommyTestTopic2"
            }
        }
    dm = { "some-config-key": minimal }

    result = dmaap.apply_defaults_dmaap_map(dm)
    assert result == {'some-config-key': {'aaf_username': None, 
        'aaf_password': None, 'dmaap_info': {'client_role': None,
            'topic_url': 'https://dcae-msrt-ftl2.com:3905/events/com.dcae.dmaap.FTL2.TommyTestTopic2', 'client_id': None, 'location': None},
        'type': 'message_router'}}


def test_update_delivery_urls():
    def get_route_with_slash(config_key):
        return "/eden"

    dmaap_map = {"spade-key": {"type": "data_router", "dmaap_info": {"delivery_url": "bleh","username": "dolittle"}},
            "clover-key": {"type": "data_router", "dmaap_info": {"publish_url": "manyfoos",
                "username": "chickenlittle"}}}

    dmaap_map = dmaap.update_delivery_urls(get_route_with_slash, "http://some-host.io", dmaap_map)

    expected = {'spade-key': {"type": "data_router", 'dmaap_info': {'delivery_url': 'http://some-host.io/eden', 
        'username': 'dolittle'}}, 'clover-key': {"type": "data_router", 'dmaap_info': {'publish_url': 'manyfoos', 
            'username': 'chickenlittle'}}}
    assert expected == dmaap_map

    def get_route_no_slash(config_key):
        return "eden"

    dmaap_map = dmaap.update_delivery_urls(get_route_no_slash, "http://some-host.io", dmaap_map)
    assert expected == dmaap_map

    # Case when there is nothing to update
    dmaap_map = {"clover-key": {"type": "data_router", "dmaap_info": {"publish_url": "manyfoos",
                "username": "chickenlittle"}}}

    assert dmaap_map == dmaap.update_delivery_urls(get_route_no_slash, "http://some-host.io", 
            dmaap_map)


def test_list_delivery_urls():
    dmaap_map = {"spade-key": {"type": "data_router", "dmaap_info": {"delivery_url": "bleh","username": "dolittle"}},
            "clover-key": {"type": "data_router", "dmaap_info": {"publish_url": "manyfoos",
                "username": "chickenlittle"}}}

    result = dmaap.list_delivery_urls(dmaap_map)
    assert result == [('spade-key', 'bleh')]
