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
Provides utilities for running components
"""
import time
import six
from functools import partial
import click
from dcae_cli.util import docker_util as du
from dcae_cli.util import dmaap, inputs
from dcae_cli.util.cdap_util import run_component as run_cdap_component
from dcae_cli.util.exc import DcaeException
from dcae_cli.util import discovery as dis
from dcae_cli.util.discovery import get_user_instances, config_context, \
    replace_dots
import dcae_cli.util.profiles as profiles
from dcae_cli.util.logger import get_logger
from dcae_cli.catalog.mock.catalog import build_config_keys_map, \
    get_data_router_subscriber_route
# This seems to be an abstraction leak
from dcae_cli.catalog.mock.schema import apply_defaults_docker_config


log = get_logger('Run')


def _get_instances(user, additional_user=None):
    instance_map = get_user_instances(user)

    if additional_user:
        # Merge current user with another user's instance map to be available to
        # connect to
        instance_map_additional = get_user_instances(additional_user)
        log.info("#Components for {0}: {1}".format(additional_user,
            len(instance_map_additional)))
        instance_map.update(instance_map_additional)

    # REVIEW: Getting instances always returns back component names with dots
    # even though the component name could originally have dots or dashes.
    # To put this dot vs dash headache to rest, we have to understand what the
    # discovery abstraction should be. Should the discovery be aware of this type
    # of naming magic? If so then the discovery abstraction may need to be
    # enhanced to be catalog aware to do name verfication queries. If not then
    # the dot-to-dash transformation might not belong inside of the discovery
    # abstraction and the higher level should do that.
    #
    # Another possible fix is to map the dots to something that's less likely to
    # be used multiple dashes. This would help disambiguate between a forced
    # mapping vs component name with dashes.
    #
    # In the meantime, here is a fix to address the issue where a downstream component
    # can't be matched when the downstream component uses dashes. This affects
    # the subsequent calls:
    #
    #   - catalog.get_discovery* query
    #   - create_config
    #
    # The instance map will contain entries where the names will be with dots and
    # with dashes. There should be no harm because only one set should match. The
    # assumption is that people won't have the same name as dots and as dashes.
    instance_map_dashes = { (replace_dots(k[0]), k[1]): v
            for k, v in six.iteritems(instance_map) }
    instance_map.update(instance_map_dashes)

    return instance_map


def _update_delivery_urls(spec, target_host, dmaap_map):
    """Updates the delivery urls for data router subscribers"""
    # Try to stick in the more appropriate delivery url which is not realized
    # until after deployment because you need the ip, port.
    # Realized that this is not actually needed by the component but kept it because
    # it might be useful for component developers to **see** this info.
    get_route_func = partial(get_data_router_subscriber_route, spec)
    target_base_url = "http://{0}".format(target_host)
    return dmaap.update_delivery_urls(get_route_func, target_base_url,
            dmaap_map)


def _verify_component(name, max_wait, consul_host):
    """Verify that the component is healthy

    Args:
    -----
    max_wait (integer): limit to how may attempts to make which translates to
        seconds because each sleep is one second. 0 means infinite.

    Return:
    -------
    True if component is healthy else returns False
    """
    num_attempts = 1

    while True:
        if dis.is_healthy(consul_host, name):
            return True
        else:
            num_attempts += 1

            if max_wait > 0 and max_wait < num_attempts:
                return False

            time.sleep(1)


def run_component(user, cname, cver, catalog, additional_user, attached, force,
        dmaap_map, inputs_map, external_ip=None):
    '''Runs a component based on the component type

    Args
    ----
    force: (boolean)
        Continue to run even when there are no valid downstream components when
        this flag is set to True.
    dmaap_map: (dict) config_key to message router or data router connections.
        Used as a manual way to make available this information for the component.
    inputs_map: (dict) config_key to value that is intended to be provided at
        deployment time as an input
    '''
    cname, cver = catalog.verify_component(cname, cver)
    ctype = catalog.get_component_type(cname, cver)
    profile = profiles.get_profile()

    instance_map = _get_instances(user, additional_user)
    neighbors = six.iterkeys(instance_map)


    dmaap_config_keys = catalog.get_discovery_for_dmaap(cname, cver)

    if not dmaap.validate_dmaap_map_entries(dmaap_map, *dmaap_config_keys):
        return

    if ctype == 'docker':
        params, interface_map = catalog.get_discovery_for_docker(cname, cver, neighbors)
        should_wait = attached

        spec = catalog.get_component_spec(cname, cver)
        config_key_map = build_config_keys_map(spec)
        inputs_map = inputs.filter_entries(inputs_map, spec)

        dmaap_map = _update_delivery_urls(spec, profile.docker_host.split(":")[0],
                dmaap_map)

        with config_context(user, cname, cver, params, interface_map,
                instance_map, config_key_map, dmaap_map=dmaap_map, inputs_map=inputs_map,
                always_cleanup=should_wait, force_config=force) as (instance_name, _):
            image = catalog.get_docker_image(cname, cver)
            docker_config = catalog.get_docker_config(cname, cver)

            docker_logins = dis.get_docker_logins()

            if should_wait:
                du.deploy_component(profile, image, instance_name, docker_config,
                        should_wait=True, logins=docker_logins)
            else:
                result = du.deploy_component(profile, image, instance_name, docker_config,
                        logins=docker_logins)
                log.debug(result)

                if result:
                    log.info("Deployed {0}. Verifying..".format(instance_name))

                    # TODO: Be smarter here but for now wait longer i.e. 5min
                    max_wait = 300 # 300s == 5min

                    if _verify_component(instance_name, max_wait, dis.consul_host):
                        log.info("Container is up and healthy")

                        # This block of code is used to construct the delivery
                        # urls for data router subscribers and to display it for
                        # users to help with manually provisioning feeds.
                        results = dis.lookup_instance(dis.consul_host, instance_name)
                        target_host = dis.parse_instance_lookup(results)

                        dmaap_map = _update_delivery_urls(spec, target_host, dmaap_map)
                        delivery_urls = dmaap.list_delivery_urls(dmaap_map)

                        if delivery_urls:
                            msg = "\n".join(["\t{k}: {url}".format(k=k, url=url)
                                for k, url in delivery_urls])
                            msg = "\n\n{0}\n".format(msg)
                            log.warn("Your component is a data router subscriber. Here are the delivery urls: {0}".format(msg))
                    else:
                        log.warn("Container never became healthy")
                else:
                    raise DcaeException("Failed to deploy docker component")

    elif ctype =='cdap':
        (jar, config, spec) = catalog.get_cdap(cname, cver)
        config_key_map = build_config_keys_map(spec)
        inputs_map = inputs.filter_entries(inputs_map, spec)

        params, interface_map = catalog.get_discovery_for_cdap(cname, cver, neighbors)

        with config_context(user, cname, cver, params, interface_map, instance_map,
                config_key_map, dmaap_map=dmaap_map, inputs_map=inputs_map, always_cleanup=False,
                force_config=force) as (instance_name, templated_conf):
            run_cdap_component(catalog, params, instance_name, profile, jar, config, spec, templated_conf)
    else:
        raise DcaeException("Unsupported component type for run")


def dev_component(user, catalog, specification, additional_user, force, dmaap_map,
        inputs_map):
    '''Sets up the discovery layer for in development component

    The passed-in component specification is
    * Validated it
    * Generates the corresponding application config
    * Pushes the application config and rels key into Consul

    This allows developers to play with their spec and the resulting configuration
    outside of being in the catalog and in a container.

    Args
    ----
    user: (string) user name
    catalog: (object) instance of MockCatalog
    specification: (dict) experimental component specification
    additional_user: (string) another user name used to source additional
        component instances
    force: (boolean)
        Continue to run even when there are no valid downstream components when
        this flag is set to True.
    dmaap_map: (dict) config_key to message router connections. Used as a
        manual way to make available this information for the component.
    inputs_map: (dict) config_key to value that is intended to be provided at
        deployment time as an input
    '''
    instance_map = _get_instances(user, additional_user)
    neighbors = six.iterkeys(instance_map)

    params, interface_map, dmaap_config_keys = catalog.get_discovery_from_spec(
            user, specification, neighbors)

    if not dmaap.validate_dmaap_map_entries(dmaap_map, *dmaap_config_keys):
        return

    cname = specification["self"]["name"]
    cver = specification["self"]["version"]
    config_key_map = build_config_keys_map(specification)
    inputs_map = inputs.filter_entries(inputs_map, specification)

    dmaap_map = _update_delivery_urls(specification, "localhost", dmaap_map)

    with config_context(user, cname, cver, params, interface_map, instance_map,
        config_key_map, dmaap_map, inputs_map=inputs_map, always_cleanup=True,
        force_config=force) \
                as (instance_name, templated_conf):

        click.echo("Ready for component development")

        if specification["self"]["component_type"] == "docker":
            # The env building is only for docker right now
            docker_config = apply_defaults_docker_config(specification["auxilary"])
            envs = du.build_envs(profiles.get_profile(), docker_config, instance_name)
            envs_message = "\n".join(["export {0}={1}".format(k, v) for k,v in envs.items()])
            envs_filename = "env_{0}".format(profiles.get_active_name())

            with open(envs_filename, "w") as f:
                f.write(envs_message)

            click.echo()
            click.echo("Setup these environment varibles. Run \"source {0}\":".format(envs_filename))
            click.echo()
            click.echo(envs_message)
            click.echo()
        else:
            click.echo("Set the following as your HOSTNAME:\n  {0}".format(instance_name))

        input("Press any key to stop and to clean up")
