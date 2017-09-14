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
Functions for DMaaP integration
"""
import six
import logging
from jsonschema import validate, ValidationError
from dcae_cli.util import reraise_with_msg
from dcae_cli.util.logger import get_logger
from dcae_cli.catalog.mock.schema import apply_defaults


logger = get_logger('Dmaap')

_SCHEMA = {
      "$schema": "http://json-schema.org/draft-04/schema#",
      "title": "Schema for dmaap inputs",
      "type": "object",
      "oneOf": [
        { "$ref": "#/definitions/message_router" },
        { "$ref": "#/definitions/data_router_publisher" },
        { "$ref": "#/definitions/data_router_subscriber" }
      ],
      "definitions": {
        "message_router": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string",
              "enum": ["message_router"]
            },
            "aaf_username": {
              "type": "string",
              "default": None
            },
            "aaf_password": {
              "type": "string",
              "default": None
            },
            "dmaap_info": {
              "type": "object",
              "properties": {
                "client_role": {
                  "type": "string",
                  "default": None
                },
                "client_id": {
                  "type": "string",
                  "default": None
                },
                "location": {
                  "type": "string",
                  "default": None
                },
                "topic_url": {
                  "type": "string"
                }
              },
              "required": [
                "topic_url"
              ],
              "additionalProperties": False
            }
          },
          "required": [
            "type",
            "dmaap_info"
          ],
          "additionalProperties": False
        },
        "data_router_publisher": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string",
              "enum": ["data_router"]
            },
            "dmaap_info": {
              "type": "object",
              "properties": {
                "location": {
                  "type": "string",
                  "default": None,
                  "description": "the DCAE location for the publisher, used to set up routing"
                },
                "publish_url": {
                  "type": "string",
                  "description": "the URL to which the publisher makes Data Router publish requests"
                },
                "log_url": {
                  "type": "string",
                  "default": None,
                  "description": "the URL from which log data for the feed can be obtained"
                },
                "username": {
                  "type": "string",
                  "default": None,
                  "description": "the username the publisher uses to authenticate to Data Router"
                },
                "password": {
                  "type": "string",
                  "default": None,
                  "description": "the password the publisher uses to authenticate to Data Router"
                },
                "publisher_id": {
                  "type": "string",
                  "default": ""
                }
              },
              "required": [
                "publish_url"
              ],
              "additionalProperties": False
            }
          },
          "required": [
            "type",
            "dmaap_info"
          ],
          "additionalProperties": False
      },
      "data_router_subscriber": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string",
              "enum": ["data_router"]
            },
            "dmaap_info": {
              "type": "object",
              "properties": {
                "location": {
                  "type": "string",
                  "default": None,
                  "description": "the DCAE location for the publisher, used to set up routing"
                },
                "delivery_url": {
                  "type": "string",
                  "description": "the URL to which the Data Router should deliver files"
                },
                "username": {
                  "type": "string",
                  "default": None,
                  "description": "the username Data Router uses to authenticate to the subscriber when delivering files"
                },
                "password": {
                  "type": "string",
                  "default": None,
                  "description": "the username Data Router uses to authenticate to the subscriber when delivering file"
                },
                "subscriber_id": {
                  "type": "string",
                  "default": ""
                }
              },
              "additionalProperties": False
            }
          },
          "required": [
            "type",
            "dmaap_info"
          ],
          "additionalProperties": False
      }
    }
}


_validation_msg = """
Is your DMaaP client object a valid json?
Does your DMaaP client object follow this format?

Message router:

    {
        "aaf_username": <string, optional>,
        "aaf_password": <string, optional>,
        "type": "message_router",
        "dmaap_info": {
            "client_role": <string, optional>,
            "client_id": <string, optional>,
            "location": <string, optional>,
            "topic_url": <string, required>
        }
    }

Data router (publisher):

    {
        "type": "data_router",
        "dmaap_info": {
            "location": <string, optional>,
            "publish_url": <string, required>,
            "log_url": <string, optional>,
            "username": <string, optional>,
            "password": <string, optional>,
            "publisher_id": <string, optional>
        }
    }

Data router (subscriber):

    {
        "type": "data_router",
        "dmaap_info": {
            "location": <string, optional>,
            "delivery_url": <string, optional>,
            "username": <string, optional>,
            "password": <string, optional>,
            "subscriber_id": <string, optional>
        }
    }

"""

def validate_dmaap_map_schema(dmaap_map):
    """Validate the dmaap map schema"""
    for k, v in six.iteritems(dmaap_map):
        try:
            validate(v, _SCHEMA)
        except ValidationError as e:
            logger.error("DMaaP validation issue with \"{k}\"".format(k=k))
            logger.error(_validation_msg)
            reraise_with_msg(e, as_dcae=True)


class DMaaPValidationError(RuntimeError):
    pass

def _find_matching_definition(instance):
    """Find and return matching definition given an instance"""
    for subsection in ["message_router", "data_router_publisher",
            "data_router_subscriber"]:
        try:
            validate(instance, _SCHEMA["definitions"][subsection])
            return _SCHEMA["definitions"][subsection]
        except ValidationError:
            pass

    # You should never get here but just in case..
    logger.error("No matching definition: {0}".format(instance))
    raise DMaaPValidationError("No matching definition")

def apply_defaults_dmaap_map(dmaap_map):
    """Apply the defaults to the dmaap map"""
    def grab_properties(instance):
        return _find_matching_definition(instance)["properties"]

    return { k: apply_defaults(grab_properties(v), v) for k,v in
            six.iteritems(dmaap_map) }


def validate_dmaap_map_entries(dmaap_map, mr_config_keys, dr_config_keys):
    """Validate dmaap map entries

    Validate dmaap map to make sure all config keys are there and that there's
    no additional config keys beceause this map is used in generating the
    configuration json.

    Returns:
    --------
    True when dmaap_map is ok and False when it is not
    """
    # Catch when there is no dmaap_map when there should be
    if len(mr_config_keys) + len(dr_config_keys) > 0 and len(dmaap_map) == 0:
        logger.error("You have dmaap streams defined in your specification")
        logger.error("You must provide a dmaap json to resolve those dmaap streams.")
        logger.error("Please use the \"--dmaap-file\" option")
        return False

    config_keys = dr_config_keys + mr_config_keys
    # Look for missing keys
    is_missing = lambda config_key: config_key not in dmaap_map
    missing_keys = list(filter(is_missing, config_keys))

    if missing_keys:
        logger.error("Missing config keys in dmaap json: {0}".format(
            ",".join(missing_keys)))
        logger.error("Re-edit your dmaap json")
        return False

    # Look for unexpected keys
    is_unexpected = lambda config_key: config_key not in config_keys
    unexpected_keys = list(filter(is_unexpected, dmaap_map.keys()))

    if unexpected_keys:
        # NOTE: Changed this to a non-error in order to support the feature of
        # developer having a master dmaap map
        logger.warn("Unexpected config keys in dmaap json: {0}".format(
            ",".join(unexpected_keys)))
        return True

    return True


def update_delivery_urls(get_route_func, target_base_url, dmaap_map):
    """Update delivery urls for dmaap map

    This method picks out all the data router connections for subscribers and
    updates the delivery urls with the supplied base target url concatentated
    with the user specified route (or path).

    Args:
    -----
    get_route_func (func): Function that takes a config_key and returns the route
        used for the data router subscriber
    target_base_url (string): "{http|https}://<hostname>:<port>"
    dmaap_map (dict): DMaaP map is map of inputs that is config_key to provisioned
        data router feed or message router topic connection details

    Returns:
    --------
    Returns the updated DMaaP map
    """
    def update_delivery_url(config_key, dm):
        route = get_route_func(config_key)
        dm["dmaap_info"]["delivery_url"] = "{base}{tween}{path}".format(base=target_base_url,
                path=route, tween="" if route[0] == "/" else "/")
        return dm

    def is_dr_subscriber(dm):
        return dm["type"] == "data_router" and "publish_url" not in dm["dmaap_info"]

    updated_map = { config_key: update_delivery_url(config_key, dm)
            for config_key, dm in six.iteritems(dmaap_map) if is_dr_subscriber(dm) }
    dmaap_map.update(updated_map)

    return dmaap_map


def list_delivery_urls(dmaap_map):
    """List delivery urls

    Returns:
    --------
    List of tuples (config_key, deliery_url)
    """
    return [(config_key, dm["dmaap_info"]["delivery_url"]) \
            for config_key, dm in six.iteritems(dmaap_map) if "delivery_url" in dm["dmaap_info"]]
