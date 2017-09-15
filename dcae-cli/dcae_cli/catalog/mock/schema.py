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
"""
Provides jsonschema
"""
import json
from functools import partial, reduce

import six
from jsonschema import validate, ValidationError
import requests

from dcae_cli.util import reraise_with_msg, fetch_file_from_web
from dcae_cli.util import config as cli_config
from dcae_cli.util.exc import DcaeException
from dcae_cli.util.logger import get_logger


log = get_logger('Schema')

# UPDATE: This message applies to the component spec which has been moved on a
# remote server.
#
# WARNING: The below has a "oneOf" for service provides, that will validate as long as any of them are chosen.
# However, this is wrong because what we really want is something like:
#     if component_type == docker
#       provides = foo
#     elif component_type == cdap
#       provides = bar
# The unlikely but problematic  case is the cdap developer gets a hold of the docker documentation, uses that, it validates, and blows up at cdap runtime


# TODO: The next step here is to decide how to manage the links to the schemas. Either:
#
#   a) Manage the links in the dcae-cli tool here and thus need to ask if this
#   belongs in the config to point to some remote server or even point to local
#   machine.
#   UPDATE: This item has been mostly completed where at least the path is configurable now.

#   b) Read the links to the schemas from the spec - self-describing jsons. Is
#   this even feasible?

#   c) Both
#

class FetchSchemaError(RuntimeError):
    pass

def _fetch_schema(schema_path):
    try:
        server_url = cli_config.get_server_url()
        return fetch_file_from_web(server_url, schema_path)
    except requests.HTTPError as e:
        raise FetchSchemaError("HTTP error from fetching schema", e)
    except Exception as e:
        raise FetchSchemaError("Unexpected error from fetching schema", e)


def _safe_dict(obj):
    '''Returns a dict from a dict or json string'''
    if isinstance(obj, str):
        return json.loads(obj)
    else:
        return obj

def _validate(fetch_schema_func, schema_path, spec):
    '''Validate the given spec

    Fetch the schema and then validate. Upon a error from fetching or validation,
    a DcaeException is raised.

    Parameters
    ----------
    fetch_schema_func: function that takes schema_path -> dict representation of schema
        throws a FetchSchemaError upon any failure
    schema_path: string - path to schema
    spec: dict or string representation of JSON of schema instance

    Returns
    -------
    Nothing, silence is golden
    '''
    try:
        schema = fetch_schema_func(schema_path)
        validate(_safe_dict(spec), schema)
    except ValidationError as e:
        reraise_with_msg(e, as_dcae=True)
    except FetchSchemaError as e:
        reraise_with_msg(e, as_dcae=True)

_validate_using_nexus = partial(_validate, _fetch_schema)


_path_component_spec = cli_config.get_path_component_spec()

def apply_defaults(properties_definition, properties):
    """Utility method to enforce expected defaults

    This method is used to enforce properties that are *expected* to have at least
    the default if not set by a user.  Expected properties are not required but
    have a default set.  jsonschema does not provide this.

    Parameters
    ----------
    properties_definition: dict of the schema definition of the properties to use
        for verifying and applying defaults
    properties: dict of the target properties to verify and apply defaults to

    Return
    ------
    dict - a new version of properties that has the expected default values
    """
    # Recursively process all inner objects. Look for more properties and not match
    # on type
    for k,v in six.iteritems(properties_definition):
        if "properties" in v:
            properties[k] = apply_defaults(v["properties"], properties.get(k, {}))

    # Collect defaults
    defaults = [ (k, v["default"]) for k, v in properties_definition.items() if "default" in v ]

    def apply_default(accumulator, default):
        k, v = default
        if k not in accumulator:
            # Not doing data type checking and any casting. Assuming that this
            # should have been taken care of in validation
            accumulator[k] = v
        return accumulator

    return reduce(apply_default, defaults, properties)

def apply_defaults_docker_config(config):
    """Apply expected defaults to Docker config
    Parameters
    ----------
    config: Docker config dict
    Return
    ------
    Updated Docker config dict
    """
    # Apply health check defaults
    healthcheck_type = config["healthcheck"]["type"]
    component_spec = _fetch_schema(_path_component_spec)

    if healthcheck_type in ["http", "https"]:
        apply_defaults_func = partial(apply_defaults,
                component_spec["definitions"]["docker_healthcheck_http"]["properties"])
    elif healthcheck_type in ["script"]:
        apply_defaults_func = partial(apply_defaults,
                component_spec["definitions"]["docker_healthcheck_script"]["properties"])
    else:
        # You should never get here
        apply_defaults_func = lambda x: x

    config["healthcheck"] = apply_defaults_func(config["healthcheck"])

    return config

def validate_component(spec):
    _validate_using_nexus(_path_component_spec, spec)

    # REVIEW: Could not determine how to do this nicely in json schema. This is
    # not ideal. We want json schema to be the "it" for validation.
    ctype = component_type = spec["self"]["component_type"]

    if ctype == "cdap":
        invalid = [s for s in spec["streams"].get("subscribes", []) \
                if s["type"] in ["data_router", "data router"]]
        if invalid:
            raise DcaeException("Cdap component as data router subscriber is not supported.")

def validate_format(spec):
    path = cli_config.get_path_data_format()
    _validate_using_nexus(path, spec)
