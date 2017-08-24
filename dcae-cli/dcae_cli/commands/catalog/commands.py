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
Queries onboarding catalog
"""
import click

from dcae_cli.commands import util


@click.group()
def catalog():
    pass


@catalog.command(name="list")
@click.option("--expanded", is_flag=True, default=False, help="Display the expanded view - show all versions and all status")
#TODO: @click.argument('query')
@click.pass_obj
def action_list(obj, expanded):
    # Query both components and data formats. Display both sets.

    user, catalog = obj['config']['user'], obj['catalog']

    only_latest = not expanded
    only_published = not expanded

    # TODO: Probably want to implement pagination
    comps = catalog.list_components(latest=only_latest, only_published=only_published)
    dfs = catalog.list_formats(latest=only_latest, only_published=only_published)

    def format_record_component(obj):
        when_published = obj["when_published"].date() \
                if obj["when_published"] else ""

        return (obj["name"], obj["version"], obj["component_type"],
                util.format_description(obj["description"]), obj["owner"],
                util.get_status_string(obj), when_published)

    comps = [ format_record_component(comp) for comp in comps ]

    click.echo("")
    click.echo("Components:")
    click.echo(util.create_table(('Name', 'Version', 'Type', 'Description', 'Owner', 'Status',
        'Published'), comps))

    def format_record_format(obj):
        when_published = obj["when_published"].date() \
                if obj["when_published"] else ""

        return (obj["name"], obj["version"],
                util.format_description(obj["description"]), obj["owner"],
                util.get_status_string(obj), when_published)

    dfs = [ format_record_format(df) for df in dfs ]

    click.echo("")
    click.echo("Data formats:")
    click.echo(util.create_table(('Name', 'Version', 'Description', 'Owner', 'Status',
        'Published'), dfs))


@catalog.command(name="show")
@click.argument("resource", metavar="name:version")
@click.pass_obj
def action_show(obj, resource):
    # Query both components and data formats. Display both sets.
    name, ver = util.parse_input(resource)
    catalog = obj['catalog']
    spec = None

    try:
        spec = catalog.get_component_spec(name, ver)

        click.echo("")
        click.echo("Component specification")
        click.echo("-----------------------")
        click.echo(util.format_json(spec))
        click.echo("")
    except:
        pass

    try:
        spec = obj['catalog'].get_format_spec(name, ver)

        click.echo("")
        click.echo("Data format")
        click.echo("-----------")
        click.echo(util.format_json(spec))
        click.echo("")
    except:
        pass

    if not spec:
        click.echo("No matching component nor data format found")
