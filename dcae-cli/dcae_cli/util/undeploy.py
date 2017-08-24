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
Provides utilities for undeploying components
"""
from functools import partial
from dcae_cli.util.exc import DcaeException
import dcae_cli.util.profiles as profiles
from dcae_cli.util.cdap_util import undeploy_component as undeploy_cdap_component
from dcae_cli.util.discovery import get_healthy_instances, get_defective_instances, \
        remove_config
from dcae_cli.util import docker_util as du
from dcae_cli.util.logger import get_logger


log = get_logger('Undeploy')


def _handler(undeploy_funcs, instances):
    """Handles the undeployment

    Executes all undeployment functions for all instances and gathers up the
    results. No short circuiting.

    Args
    ----
    undeploy_funcs: List of functions that have the following signature `fn: string->boolean`
        the input is a fully qualified instance name and the return is True upon
        success and False for failures
    instances: List of fully qualified instance names

    Returns
    -------
    (failures, results) where each are a list of tuples.  Each tuple has the
    structure: `(<instance name>, result of func 1, result of func 2, ..)`.
    """
    if not instances:
        return [], []

    # Invoke all undeploy funcs for all instances
    def invoke_undeploys(instance):
        return tuple([ undeploy_func(instance) for undeploy_func in undeploy_funcs ])

    results = [ (instance, ) + invoke_undeploys(instance) for instance in instances ]

    # Determine failures
    filter_failures_func = partial(filter, lambda result: not all(result[1:]))
    failures = list(filter_failures_func(results))

    return failures, results


def _handler_report(failures, results):
    """Reports the result of handling"""
    if len(failures) > 0:
        failed_names = [ result[0] for result in failures ]
        log.warn("Could not completely undeploy: {0}".format(", ".join(failed_names)))

        # This message captures a case where you are seeing a false negative. If
        # you attempted to undeploy a component instance and it partially failed
        # the first time but "succeeded" the second time, the second undeploy
        # would get reported as a failure. The second undeploy would probably
        # also be partial undeploy because the undeploy operation that succeeded
        # the first time will fail the second time.
        log.warn("NOTE: This could be expected since we are attempting to undeploy a component in a bad partial state")
    elif len(results) == 0:
        log.warn("No components found to undeploy")
    else:
        # This seems like important info so set it to warning so that it shows up
        log.warn("Undeployed components: {0}".format(len(results)))


def undeploy_component(user, cname, cver, catalog):
    '''Undeploys a component based on the component type'''
    cname, cver = catalog.verify_component(cname, cver)
    ctype = catalog.get_component_type(cname, cver)
    profile = profiles.get_profile()
    # Get *all* instances of the component whether running healthy or in a bad partial
    # deployed state
    instances = get_healthy_instances(user, cname, cver) + get_defective_instances(user, cname, cver)

    if ctype == 'docker':
        client = du.get_docker_client(profile)
        image = catalog.get_docker_image(cname, cver)
        undeploy_func = partial(du.undeploy_component, client, image)
    elif ctype == 'cdap':
        undeploy_func = partial(undeploy_cdap_component, profile)
    else:
        raise DcaeException("Unsupported component type for undeploy")

    log.warn("Undeploying components: {0}".format(len(instances)))
    _handler_report(*_handler([undeploy_func, remove_config], instances))
