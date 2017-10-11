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
Provides Consul helper functions
"""
import re
import json
import contextlib
from collections import defaultdict
from itertools import chain
from functools import partial
from uuid import uuid4

import six
from copy import deepcopy
from consul import Consul

from dcae_cli.util.logger import get_logger
from dcae_cli.util.exc import DcaeException
from dcae_cli.util.profiles import get_profile
from dcae_cli.util.config import get_docker_logins_key


logger = get_logger('Discovery')

active_profile = get_profile()
consul_host = active_profile.consul_host
# NOTE: Removed the suffix completely. The useful piece of the suffix was the
# location but it was implemented in a static fashion (hardcoded). Rather than
# enhancing the existing approach and making the suffix dynamic (to support
# "rework-central" and "solutioning"), the thinking is to revisit this name stuff
# and use Consul's query interface so that location is a tag attribute.
_inst_re = re.compile(r"^(?P<user>[^.]*).(?P<hash>[^.]*).(?P<ver>\d+-\d+-\d+).(?P<comp>.*)$")


class DiscoveryError(DcaeException):
    pass

class DiscoveryNoDownstreamComponentError(DiscoveryError):
    pass


def replace_dots(comp_name, reverse=False):
    '''Converts dots to dashes to prevent downstream users of Consul from exploding'''
    if not reverse:
        return comp_name.replace('.', '-')
    else:
        return comp_name.replace('-', '.')

# Utility functions for using Consul

def _is_healthy_pure(get_health_func, instance):
    """Checks to see if a component instance is running healthy

    Pure function edition

    Args
    ----
    get_health_func: func(string) -> complex object
        Look at unittests in test_discovery to see examples
    instance: (string) fully qualified name of component instance

    Returns
    -------
    True if instance has been found and is healthy else False
    """
    index, resp = get_health_func(instance)

    if resp:
        def is_passing(instance):
            return all([check["Status"] == "passing" for check in instance["Checks"]])
        return any([is_passing(instance) for instance in resp])
    else:
        return False

def is_healthy(consul_host, instance):
    """Checks to see if a component instance is running healthy

    Impure function edition

    Args
    ----
    consul_host: (string) host string of Consul
    instance: (string) fully qualified name of component instance

    Returns
    -------
    True if instance has been found and is healthy else False
    """
    cons = Consul(consul_host)
    return _is_healthy_pure(cons.health.service, instance)

def _get_instances_from_kv(get_from_kv_func, user):
    """Get component instances from kv store

    Deployed component instances get entries in a kv store to store configuration
    information. This is a way to source a list of component instances that were
    attempted to run. A component could have deployed but failed to register itself.
    The only trace of that deployment would be checking the kv store.

    Args
    ----
    get_from_kv_func: func(string, boolean) -> (don't care, list of dicts)
        Look at unittests in test_discovery to see examples
    user: (string) user id

    Returns
    -------
    List of unique component instance names
    """
    # Keys from KV contain rels key entries and non-rels key entries. Keep the
    # rels key entries but remove the ":rel" suffix because we are paranoid that
    # this could exist without the other
    _, instances_kv = get_from_kv_func(user, recurse=True)
    return [] if instances_kv is None \
            else list(set([ dd["Key"].replace(":rel", "") for dd in instances_kv ]))

def _get_instances_from_catalog(get_from_catalog_func, user):
    """Get component instances from catalog

    Fetching instances from the catalog covers the deployment cases where
    components registered successfully regardless of their health check status.

    Args
    ----
    get_from_catalog_func: func() -> (don't care, dict)
        Look at unittests in test_discovery to see examples
    user: (string) user id

    Returns
    -------
    List of unique component instance names
    """
    # Get all services and filter here by user
    response = get_from_catalog_func()
    return list(set([ instance for instance in response[1].keys() if user in instance ]))

def _merge_instances(user, *get_funcs):
    """Merge the result of an arbitrary list of get instance function calls

    Args
    ----
    user: (string) user id
    get_funcs: func(string) -> list of strings
        Functions that take in a user parameter to output a list of instance
        names

    Returns
    -------
    List of unique component instance names
    """
    return list(set(chain.from_iterable([ get_func(user) for get_func in get_funcs ])))

def _get_instances(consul_host, user):
    """Get all deployed component instances for a given user

    Sourced from multiple places to ensure we get a complete list of all
    component instances no matter what state they are in.

    Args
    ----
    consul_host: (string) host string of Consul
    user: (string) user id

    Returns
    -------
    List of unique component instance names
    """
    cons = Consul(consul_host)

    get_instances_from_kv = partial(_get_instances_from_kv, cons.kv.get)
    get_instances_from_catalog = partial(_get_instances_from_catalog, cons.catalog.services)

    return _merge_instances(user, get_instances_from_kv, get_instances_from_catalog)


# Custom (sometimes higher order) "discovery" functionality

def _make_instances_map(instances):
    """Make an instance map

    Instance map is a dict where the keys are tuples (component type, component version)
    that map to a set of strings that are instance names.
    """
    mapping = defaultdict(set)
    for instance in instances:
        match = _inst_re.match(instance)
        if match is None:
            continue

        _, _, ver, comp = match.groups()
        cname = replace_dots(comp, reverse=True)
        version = replace_dots(ver, reverse=True)
        key = (cname, version)
        mapping[key].add(instance)
    return mapping


def get_user_instances(user, consul_host=consul_host, filter_instances_func=is_healthy):
    '''Get a user's instance map

    Args:
    -----
    filter_instances_func: fn(consul_host, instance) -> boolean
        Function used to filter instances. Default is is_healthy

    Returns:
    --------
    Dict whose keys are component (name,version) tuples and values are list of component instance names
    '''
    filter_func = partial(filter_instances_func, consul_host)
    instances = list(filter(filter_func, _get_instances(consul_host, user)))

    return _make_instances_map(instances)


def _get_component_instances(filter_instances_func, user, cname, cver, consul_host):
    """Get component instances that are filtered

    Args:
    -----
    filter_instances_func: fn(consul_host, instance) -> boolean
        Function used to filter instances

    Returns
    -------
    List of strings where the strings are fully qualified instance names
    """
    instance_map = get_user_instances(user, consul_host=consul_host,
            filter_instances_func=filter_instances_func)

    # REVIEW: We don't restrict component names from using dashes. We do
    # transform names with dots to use dashes for domain segmenting reasons.
    # Instance map creation always reverses that making dashes to dots even though
    # the component name may have dashes. Thus always search for instances by
    # a dotted component name. We are open to a collision but that is low chance
    # - someone has to use the same name in dotted and dashed form which is weird.
    cname_dashless = replace_dots(cname, reverse=True)

    # WATCH: instances_map.get returns set. Force to be list to have consistent
    # return
    return list(instance_map.get((cname_dashless, cver), []))

def get_healthy_instances(user, cname, cver, consul_host=consul_host):
    """Lists healthy instances of a particular component for a given user

    Returns
    -------
    List of strings where the strings are fully qualified instance names
    """
    return _get_component_instances(is_healthy, user, cname, cver, consul_host)

def get_defective_instances(user, cname, cver, consul_host=consul_host):
    """Lists *not* running instances of a particular component for a given user

    This means that there are component instances that are sitting out there
    deployed but not successfully running.

    Returns
    -------
    List of strings where the strings are fully qualified instance names
    """
    def is_not_healthy(consul_host, component):
        return not is_healthy(consul_host, component)

    return _get_component_instances(is_not_healthy, user, cname, cver, consul_host)


def lookup_instance(consul_host, name):
    """Query Consul for service details"""
    cons = Consul(consul_host)
    index, results = cons.catalog.service(name)
    return results

def parse_instance_lookup(results):
    """Parse the resultset from lookup_instance

    Returns:
    --------
    String in host form <address>:<port>
    """
    if results:
        # Just grab first
        result = results[0]
        return "{address}:{port}".format(address=result["ServiceAddress"],
                port=result["ServicePort"])
    else:
        return


def _create_rels_key(config_key):
    """Create rels key from config key

    Assumes config_key is well-formed"""
    return "{:}:rel".format(config_key)


def _create_dmaap_key(config_key):
    """Create dmaap key from config key

    Assumes config_key is well-formed"""
    return "{:}:dmaap".format(config_key)


def clear_user_instances(user, host=consul_host):
    '''Removes all Consul key:value entries for a given user'''
    cons = Consul(host)
    cons.kv.delete(user, recurse=True)


_multiple_compat_msg = '''Component '{cname}' config_key '{ckey}' has multiple compatible downstream \
components: {compat}. The current infrastructure can only support interacing with a single component. \
Only downstream component '{chosen}' will be connected.'''

_no_compat_msg = "Component '{cname}' config_key '{ckey}' has no compatible downstream components."

_no_inst_msg = '''Component '{cname}' config_key '{ckey}' is compatible with downstream component '{chosen}' \
however there are no instances available for connecting.'''


def _cfmt(*args):
    '''Returns a string formatted representation for a component and version'''
    if len(args) == 1:
        return ':'.join(args[0])
    elif len(args) == 2:
        return ':'.join(args)
    else:
        raise DiscoveryError('Input should be name, version or (name, version)')


def _get_downstream(cname, cver, config_key, compat_comps, instance_map,
        force=False):
    '''
    Returns a component type and its instances to use for a given config key

    Parameters
    ----------
    cname : string
        Name of the upstream component
    cver : string
        Version of the upstream component
    config_key : string
        Mainly used for populating warnings meaningfully
    compat_comps : dict
        A list of component (name, version) tuples
    instance_map : dict
        A dict whose keys are component (name, version) tuples and values are a list of instance names
    '''
    if not compat_comps:
        conn_comp = ('', '')
        logger.warning(_no_compat_msg.format(cname=_cfmt(cname, cver), ckey=config_key))
    else:
        conn_comp = six.next(iter(compat_comps))
        if len(compat_comps) > 1:
            logger.warning(_multiple_compat_msg.format(cname=_cfmt(cname, cver), ckey=config_key,
                                                       compat=list(map(_cfmt, compat_comps)), chosen=_cfmt(conn_comp)))
    if all(conn_comp):
        instances = instance_map.get(conn_comp, tuple())
        if not instances:
            if force:
                logger.warning(_no_inst_msg.format(cname=_cfmt(cname, cver), \
                        ckey=config_key, chosen=_cfmt(conn_comp)))
            else:
                logger.error(_no_inst_msg.format(cname=_cfmt(cname, cver), \
                        ckey=config_key, chosen=_cfmt(conn_comp)))
                raise DiscoveryNoDownstreamComponentError("No compatible downstream component found.")
    else:
        instances = tuple()

    return conn_comp, instances


def create_config(user, cname, cver, params, interface_map, instance_map, dmaap_map,
        instance_prefix=None, force=False):
    '''
    Creates a config and corresponding rels entries in Consul. Returns the Consul the keys and entries.

    Parameters
    ----------
    user : string
        The user namespace to create the config and rels under. E.g. user.foo.bar...
    cname : string
        Name of the upstream component
    cver : string
        Version of the upstream component
    params : dict
        Parameters of the component, taken directly from the component specification
    interface_map : dict
        A dict mapping the config_key of published streams and/or called services to a list of compatible
        component types and versions
    instance_map : dict
        A dict mapping component types and versions to a list of instances currently running
    dmaap_map : dict
        A dict that contains config key to dmaap information. This map is checked
        first before checking the instance_map which means before checking for
        direct http components.
    instance_prefix : string, optional
        The unique prefix to associate with the component instance whose config is being created
    force: string, optional
        Config will continue to be created even if there are no downstream compatible
        component when this flag is set to True. Default is False.
    '''
    inst_pref = str(uuid4()) if instance_prefix is None else instance_prefix
    conf_key = "{:}.{:}.{:}.{:}".format(user, inst_pref, replace_dots(cver), replace_dots(cname))
    rels_key = _create_rels_key(conf_key)
    dmaap_key = _create_dmaap_key(conf_key)

    conf = params.copy()
    rels = list()

    # NOTE: The dmaap_map entries are broken up between the templetized config
    # and the dmaap json in Consul
    for config_key, dmaap_goodies in six.iteritems(dmaap_map):
        conf[config_key] = deepcopy(dmaap_map[config_key])
        # Here comes the magic. << >> signifies dmaap to downstream config
        # binding service.
        conf[config_key]["dmaap_info"] = "<<{:}>>".format(config_key)

    # NOTE: The interface_map may not contain *all* possible interfaces
    # that may be connected with because the catalog.get_discovery call filters
    # based upon neighbors. Essentailly the interface_map is being pre-filtered
    # which is probably a latent bug.

    for config_key, compat_types in six.iteritems(interface_map):
        # Don't clobber config keys that have been set from above
        if config_key not in conf:
            conn_comp, instances = _get_downstream(cname, cver, config_key, \
                    compat_types, instance_map, force=force)
            conn_name, conn_ver = conn_comp
            middle = ''

            if conn_name and conn_ver:
                middle = "{:}.{:}".format(replace_dots(conn_ver), replace_dots(conn_name))
            else:
                if not force:
                    raise DiscoveryNoDownstreamComponentError("No compatible downstream component found.")

            config_val = '{{' + middle + '}}'
            conf[config_key] = config_val
            rels.extend(instances)

    dmaap_map_just_info = { config_key: v["dmaap_info"]
            for config_key, v in six.iteritems(dmaap_map) }
    return conf_key, conf, rels_key, rels, dmaap_key, dmaap_map_just_info


def get_docker_logins(host=consul_host):
    """Get Docker logins from Consul

    Returns
    -------
    List of objects where the objects must be of the form
        {"registry": .., "username":.., "password":.. }
    """
    key = get_docker_logins_key()
    (index, val) = Consul(host).kv.get(key)

    if val:
        return json.loads(val['Value'].decode("utf-8"))
    else:
        return []


def push_config(conf_key, conf, rels_key, rels, dmaap_key, dmaap_map, host=consul_host):
    '''Uploads the config and rels to Consul'''
    cons = Consul(host)
    for k, v in ((conf_key, conf), (rels_key, rels), (dmaap_key, dmaap_map)):
        cons.kv.put(k, json.dumps(v))


def remove_config(config_key, host=consul_host):
    """Deletes a config from Consul

    Returns
    -------
    True when all artifacts have been successfully deleted else False
    """
    cons = Consul(host)
    results = [ cons.kv.delete(k) for k in (config_key, _create_rels_key(config_key), \
            _create_dmaap_key(config_key)) ]
    return all(results)


def _group_config(config, config_key_map):
    """Groups config by streams_publishes, streams_subscribes, services_calls"""
    # Copy non streams and services first
    grouped_conf = { k: v for k,v in six.iteritems(config)
            if k not in config_key_map }

    def group(group_name):
        grouped_conf[group_name] = { k: v for k,v in six.iteritems(config)
            if k in config_key_map and config_key_map[k]["group"] == group_name }

    # Copy and group the streams and services
    # Map returns iterator so must force running its course
    list(map(group, ["streams_publishes", "streams_subscribes", "services_calls"]))
    return grouped_conf


def _apply_inputs(config, inputs_map):
    """Update configuration with inputs

    This method updates the values of the configuration parameters using values
    from the inputs map.
    """
    config.update(inputs_map)
    return config


@contextlib.contextmanager
def config_context(user, cname, cver, params, interface_map, instance_map,
        config_key_map, dmaap_map={}, inputs_map={}, instance_prefix=None,
        host=consul_host, always_cleanup=True, force_config=False):
    '''Convenience utility for creating configs and cleaning them up

    Args
    ----
    always_cleanup: (boolean) This context manager will cleanup the produced config
        context always if this is True. When False, cleanup will only occur upon any
        exception getting thrown in the context manager block. Default is True.
    force: (boolean)
        Config will continue to be created even if there are no downstream compatible
        component when this flag is set to True. Default is False.
    '''
    try:
        conf_key, conf, rels_key, rels, dmaap_key, dmaap_map = create_config(
                user, cname, cver, params, interface_map, instance_map, dmaap_map,
                instance_prefix, force=force_config)

        conf = _apply_inputs(conf, inputs_map)
        conf = _group_config(conf, config_key_map)

        push_config(conf_key, conf, rels_key, rels, dmaap_key, dmaap_map, host)
        yield (conf_key, conf)
    except Exception as e:
        if not always_cleanup:
            try:
                conf_key, rels_key, host
            except UnboundLocalError:
                pass
            else:
                remove_config(conf_key, host)

        raise e
    finally:
        if always_cleanup:
            try:
                conf_key, rels_key, host
            except UnboundLocalError:
                pass
            else:
                remove_config(conf_key, host)
