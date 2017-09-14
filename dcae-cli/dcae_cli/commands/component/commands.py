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
Provides component commands
"""
import json
from pprint import pformat

import click

from discovery_client import resolve_name

from dcae_cli.util import profiles, load_json, dmaap, inputs
from dcae_cli.util.run import run_component, dev_component
from dcae_cli.util import discovery as dis
from dcae_cli.util.discovery import DiscoveryNoDownstreamComponentError
from dcae_cli.util.undeploy import undeploy_component
from dcae_cli.util.exc import DcaeException
from dcae_cli.commands import util
from dcae_cli.commands.util import parse_input, parse_input_pair, create_table

from dcae_cli.catalog.exc import MissingEntry


@click.group()
def component():
    pass


@component.command(name='list')
@click.option('--latest', is_flag=True, default=True, help='Only list the latest version of components which match the filter criteria')
@click.option('--subscribes', '-sub', multiple=True, help='Only list components which subscribe to FORMAT')
@click.option('--publishes', '-pub', multiple=True, help='Only list components which publish FORMAT')
@click.option('--provides', '-pro', multiple=True, type=(str, str), help='Only list components which provide services REQ_FORMAT RESP_FORMAT')
@click.option('--calls', '-cal', multiple=True, type=(str, str), help='Only list components which call services REQ_FORMAT RESP_FORMAT')
@click.option('--deployed', is_flag=True, default=False, help='Display the deployed view. Shows details of deployed instances.')
@click.pass_obj
def list_component(obj, latest, subscribes, publishes, provides, calls, deployed):
    '''Lists components in the public catalog. Uses flags to filter results.'''
    subs = list(map(parse_input, subscribes)) if subscribes else None
    pubs = list(map(parse_input, publishes)) if publishes else None
    provs = list(map(parse_input_pair, provides)) if provides else None
    cals = list(map(parse_input_pair, calls)) if calls else None

    user, catalog = obj['config']['user'], obj['catalog']
    # TODO: How about components that you don't own but you have deployed?
    comps = catalog.list_components(subs, pubs, provs, cals, latest, user=user)

    active_profile = profiles.get_profile()
    consul_host = active_profile.consul_host

    click.echo("Active profile: {0}".format(profiles.get_active_name()))
    click.echo("")

    def format_resolve_results(results):
        """Format the results from the resolve_name function call"""
        if results:
            # Most likely the results will always be length one until we migrate
            # to a different way of registering names
            return "\n".join([ pformat(result) for result in results ])
        else:
            return None

    def get_instances_as_rows(comp):
        """Get all deployed running instances of a component plus details about
        those instances and return as a list of rows"""
        cname = comp["name"]
        cver = comp["version"]
        ctype = comp["component_type"]

        instances = dis.get_healthy_instances(user, cname, cver)
        instances_status = ["Healthy"]*len(instances)
        instances_conns = [ format_resolve_results(resolve_name(consul_host, instance)) \
                for instance in instances ]

        instances_defective = dis.get_defective_instances(user, cname, cver)
        instances_status += ["Defective"]*len(instances_defective)
        instances_conns += [""]*len(instances_defective)

        instances += instances_defective

        return list(zip(instances, instances_status, instances_conns))

    # Generate grouped rows where a grouped row is (name, version, type, [instances])
    grouped_rows = [ (comp, get_instances_as_rows(comp)) for comp in comps ]

    # Display
    if deployed:
        def display_deployed(comp, instances):
            cname = comp["name"]
            cver = comp["version"]
            ctype = comp["component_type"]

            click.echo("Name: {0}".format(cname))
            click.echo("Version: {0}".format(cver))
            click.echo("Type: {0}".format(ctype))
            click.echo(create_table(('Instance', 'Status', 'Connection'), instances))
            click.echo("")

        [ display_deployed(*row) for row in grouped_rows ]
    else:
        def format_row(comp, instances):
            return comp["name"], comp["version"], comp["component_type"], \
                util.format_description(comp["description"]), \
                util.get_status_string(comp), comp["modified"], len(instances)

        rows = [ format_row(*grouped_row) for grouped_row in grouped_rows ]
        click.echo(create_table(('Name', 'Version', 'Type', 'Description',
            'Status', 'Modified', '#Deployed'), rows))
        click.echo("\nUse the \"--deployed\" option to see more details on deployments")


@component.command()
@click.argument('component', metavar="name:version")
@click.pass_obj
def show(obj, component):
    '''Provides more information about COMPONENT'''
    cname, cver = parse_input(component)
    catalog = obj['catalog']
    comp_spec = catalog.get_component_spec(cname, cver)

    click.echo(util.format_json(comp_spec))


_help_dmaap_file = """
Path to a file that contains a json of dmaap client information.  The structure of the json is expected to be:

  {
    <config_key1>: {..client object 1..},
    <config_key2>: {..client object 2..},
    ...
  }

Where "client object" can be for message or data router. The "config_key" matches the value of specified in the message router "streams" in the component specification.

Please refer to the documentation for examples of "client object".
"""

def _parse_dmaap_file(dmaap_file):
    try:
        with open(dmaap_file, 'r+') as f:
            dmaap_map = json.load(f)
            dmaap.validate_dmaap_map_schema(dmaap_map)
            return dmaap.apply_defaults_dmaap_map(dmaap_map)
    except Exception as e:
        message = "Problems with parsing the dmaap file. Check to make sure that it is a valid json and is in the expected structure."
        raise DcaeException(message)

_help_inputs_file = """
Path to a file that contains a json that contains values to be used to bind to configuration parameters that have been marked as "sourced_at_deployment". The structure of the json is expected to be:

 {
   <parameter1 name>: value,
   <parameter2 name>: value
 }

The "parameter name" is the value of the "name" property for the given configuration parameter.
"""

def _parse_inputs_file(inputs_file):
    try:
        with open(inputs_file, 'r+') as f:
            inputs_map = json.load(f)
            # TODO: Validation of schema in the future? Skipping this because
            # dti_payload is not being intended to be used.
            return inputs_map
    except Exception as e:
        message = "Problems with parsing the inputs file. Check to make sure that it is a valid json and is in the expected structure."
        raise DcaeException(message)


@component.command()
@click.option('--external-ip', '-ip', default=None, help='The external IP address of the Docker host. Only used for Docker components.')
@click.option('--additional-user', default=None, help='Additional user to grab instances from.')
@click.option('--attached', is_flag=True, help='(Docker) dcae-cli deploys then attaches to the component when set')
@click.option('--force', is_flag=True, help='Force component to run without valid downstream dependencies')
@click.option('--dmaap-file', type=click.Path(resolve_path=True, exists=True, dir_okay=False),
        help=_help_dmaap_file)
@click.option('--inputs-file', type=click.Path(resolve_path=True, exists=True, dir_okay=False),
        help=_help_inputs_file)
@click.argument('component')
@click.pass_obj
def run(obj, external_ip, additional_user, attached, force, dmaap_file, component,
        inputs_file):
    '''Runs the latest version of COMPONENT. You may optionally specify version via COMPONENT:VERSION'''
    cname, cver = parse_input(component)
    user, catalog = obj['config']['user'], obj['catalog']

    dmaap_map = _parse_dmaap_file(dmaap_file) if dmaap_file else {}
    inputs_map = _parse_inputs_file(inputs_file) if inputs_file else {}

    try:
        run_component(user, cname, cver, catalog, additional_user, attached, force,
                dmaap_map, inputs_map, external_ip)
    except DiscoveryNoDownstreamComponentError as e:
        message = "Either run a compatible downstream component first or run with the --force flag to ignore this error"
        raise DcaeException(message)
    except inputs.InputsValidationError as e:
        click.echo("There is a problem. {0}".format(e))
        message = "Component requires inputs. Please look at the use of --inputs-file and make sure the format is correct"
        raise DcaeException(message)

@component.command()
@click.argument('component')
@click.pass_obj
def undeploy(obj,  component):
    '''Undeploys the latest version of COMPONENT. You may optionally specify version via COMPONENT:VERSION'''
    cname, cver = parse_input(component)
    user, catalog = obj['config']['user'], obj['catalog']
    undeploy_component(user, cname, cver, catalog)


@component.command()
@click.argument('specification', type=click.Path(resolve_path=True, exists=True))
@click.option('--additional-user', default=None, help='Additional user to grab instances from.')
@click.option('--force', is_flag=True, help='Force component to run without valid downstream dependencies')
@click.option('--dmaap-file', type=click.Path(resolve_path=True, exists=True, dir_okay=False),
        help=_help_dmaap_file)
@click.option('--inputs-file', type=click.Path(resolve_path=True, exists=True, dir_okay=False),
        help=_help_inputs_file)
@click.pass_obj
def dev(obj, specification, additional_user, force, dmaap_file, inputs_file):
    '''Set up component in development for discovery, use for local development'''
    user, catalog = obj['config']['user'], obj['catalog']

    dmaap_map = _parse_dmaap_file(dmaap_file) if dmaap_file else {}
    inputs_map = _parse_inputs_file(inputs_file) if inputs_file else {}

    with open(specification, 'r+') as f:
        spec = json.loads(f.read())
        try:
            dev_component(user, catalog, spec, additional_user, force, dmaap_map,
                    inputs_map)
        except DiscoveryNoDownstreamComponentError as e:
            message = "Either run a compatible downstream component first or run with the --force flag to ignore this error"
            raise DcaeException(message)
        except inputs.InputsValidationError as e:
            click.echo("There is a problem. {0}".format(e))
            message = "Component requires inputs. Please look at the use of --inputs-file and make sure the format is correct"
            raise DcaeException(message)


@component.command()
@click.argument('component')
@click.pass_obj
def publish(obj, component):
    """Pushes COMPONENT to the public catalog"""
    name, version = parse_input(component)
    user, catalog = obj['config']['user'], obj['catalog']

    try:
        # Dependent data formats must be published first before publishing
        # component. Check that here
        unpub_formats = catalog.get_unpublished_formats(name, version)

        if unpub_formats:
            click.echo("You must publish dependent data formats first:")
            click.echo("")
            click.echo("\n".join([":".join(uf) for uf in unpub_formats]))
            click.echo("")
            return
    except MissingEntry as e:
        raise DcaeException("Component not found")

    if catalog.publish_component(user, name, version):
        click.echo("Component has been published")
    else:
        click.echo("Component could not be published")


@component.command()
@click.option('--update', is_flag=True, help='Updates a locally added component if it has not been already pushed')
@click.argument('specification', type=click.Path(resolve_path=True, exists=True))
@click.pass_obj
def add(obj, update, specification):
    user, catalog = obj['config']['user'], obj['catalog']

    spec = load_json(specification)
    catalog.add_component(user, spec, update)
