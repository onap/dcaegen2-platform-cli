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
Provides utilities for Docker components
"""
import socket
from sys import platform

import docker
import six

import dockering as doc
from dcae_cli.util.logger import get_logger
from dcae_cli.util.exc import DcaeException


dlog = get_logger('Docker')

_reg_img = 'gliderlabs/registrator:latest'
# TODO: Source this from app's configuration [ONAP URL TBD]
_reg_cmd = '-ip {:} consul://make-me-valid:8500'

class DockerError(DcaeException):
    pass

class DockerConstructionError(DcaeException):
    pass


# Functions to provide envs to pass into Docker containers

def _convert_profile_to_docker_envs(profile):
    """Convert a profile object to Docker environment variables

    Parameters
    ----------
    profile: namedtuple

    Returns
    -------
    dict of environemnt variables to be used by docker-py
    """
    profile = profile._asdict()
    return dict([(key.upper(), value) for key, value in six.iteritems(profile)])


def build_envs(profile, docker_config, instance_name):
    profile_envs = _convert_profile_to_docker_envs(profile)
    health_envs = doc.create_envs_healthcheck(docker_config)
    return doc.create_envs(instance_name, profile_envs, health_envs)


# Methods to call Docker engine

# TODO: Consolidate these two docker client methods. Need ability to invoke local
# vs remote Docker engine

def get_docker_client(profile, logins=[]):
    hostname, port = profile.docker_host.split(":")
    try:
        client = doc.create_client(hostname, port, logins=logins)
        client.ping()
        return client
    except:
        raise DockerError('Could not connect to the Docker daemon. Is it running?')

def _get_docker_client(client_funcs=(docker.Client, docker.from_env)):
    '''Returns a docker client object'''
    for func in client_funcs:
        try:
            client = func(version='auto')
            client.ping()
            return client
        except:
            continue
    raise DockerError('Could not connect to the Docker daemon. Is it running?')


def image_exists(image):
    '''Returns True if the image exists locally'''
    client = _get_docker_client()
    return True if client.images(image) else False


def _infer_ip():
    '''Infers the IP address of the host running this tool'''
    if not platform.startswith('linux'):
        raise DockerError('Non-linux environment detected. Use the --external-ip flag when running Docker components.')
    ip = socket.gethostbyname(socket.gethostname())
    dlog.info("Docker host external IP address inferred to be {:}. If this is incorrect, use the --external-ip flag.".format(ip))
    return ip


def _run_container(client, config, name=None, wait=False):
    '''Runs a container'''
    if name is not None:
        info = six.next(iter(client.containers(all=True, filters={'name': "^/{:}$".format(name)})), None)
        if info is not None:
            if info['State'] == 'running':
                dlog.info("Container '{:}' was detected as already running.".format(name))
                return info
            else:
                client.remove_container(info['Id'])

    cont = doc.create_container_using_config(client, name, config)
    client.start(cont)
    info = client.inspect_container(cont)
    name = info['Name'][1:]  # remove '/' prefix
    image = config['Image']
    dlog.info("Running image '{:}' as '{:}'".format(image, name))

    if not wait:
        return info

    cont_log = dlog.getChild(name)
    try:
        for msg in client.logs(cont, stream=True):
            cont_log.info(msg.decode())
        else:
            dlog.info("Container '{:}' exitted suddenly.".format(name))
    except (KeyboardInterrupt, SystemExit):
        dlog.info("Stopping container '{:}' and cleaning up...".format(name))
        client.kill(cont)
        client.remove_container(cont)


def _run_registrator(client, external_ip=None):
    '''Ensures that Registrator is running'''

    ip = _infer_ip() if external_ip is None else external_ip
    cmd = _reg_cmd.format(ip).split()

    binds={'/var/run/docker.sock': {'bind': '/tmp/docker.sock'}}
    hconf = client.create_host_config(binds=binds, network_mode='host')
    conf = client.create_container_config(image=_reg_img, command=cmd, host_config=hconf)

    _run_container(client, conf, name='registrator', wait=False)


# TODO: Need to revisit and reimplement _run_registrator(client, external_ip)

#
# High level calls
#

def deploy_component(profile, image, instance_name, docker_config, should_wait=False,
        logins=[]):
    """Deploy Docker component

    This calls runs a Docker container detached.  The assumption is that the Docker
    host already has registrator running.

    TODO: Split out the wait functionality

    Args
    ----
    logins (list): List of objects where the objects are each a docker login of
    the form:

        {"registry": .., "username":.., "password":.. }

    Returns
    -------
    Dict that is the result from a Docker inspect call
    """
    ports = docker_config.get("ports", None)
    hcp = doc.add_host_config_params_ports(ports=ports)
    volumes = docker_config.get("volumes", None)
    hcp = doc.add_host_config_params_volumes(volumes=volumes, host_config_params=hcp)
    # Thankfully passing in an IP will return back an IP
    dh = profile.docker_host.split(":")[0]
    _, _, dhips = socket.gethostbyname_ex(dh)

    if dhips:
        hcp = doc.add_host_config_params_dns(dhips[0], hcp)
    else:
        raise DockerConstructionError("Could not resolve the docker hostname:{0}".format(dh))

    envs = build_envs(profile, docker_config, instance_name)
    client = get_docker_client(profile, logins=logins)

    config = doc.create_container_config(client, image, envs, hcp)
    return _run_container(client, config, name=instance_name, wait=should_wait)


def undeploy_component(client, image, instance_name):
    """Undeploy Docker component

    TODO: Handle error scenarios. Look into:
    * no container found error - docker.errors.NotFound
    * failure to remove image - docker.errors.APIError: 409 Client Error
    * retry, check for still running container

    Returns
    -------
    True if the container and associated image has been removed False otherwise
    """
    try:
        client.remove_container(instance_name, force=True)
        client.remove_image(image)
        return True
    except Exception as e:
        dlog.error("Error while undeploying Docker container/image: {0}".format(e))
        return False
