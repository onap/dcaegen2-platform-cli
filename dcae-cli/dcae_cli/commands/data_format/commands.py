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
Provides data format commands
"""
import json

import click

from dcae_cli.util import load_json
from dcae_cli.util.logger import get_logger
from dcae_cli.commands import util
from dcae_cli.commands.util import create_table, parse_input

from dcae_cli.catalog.exc import MissingEntry


logger = get_logger('DataFormatCommand')


@click.group()
def data_format():
    pass


@data_format.command()
@click.option('--update', is_flag=True, help='Updates a locally added data format if it has not been already pushed')
@click.argument('specification', type=click.Path(resolve_path=True, exists=True))
@click.pass_obj
def add(obj, update, specification):
    '''Tracks a data format file SPECIFICATION locally but does not push to the catalog'''
    spec = load_json(specification)
    user, catalog = obj['config']['user'], obj['catalog']
    catalog.add_format(spec, user, update)


@data_format.command(name='list')
@click.option('--latest', is_flag=True, help='Only list the latest version of data formats')
@click.pass_obj
def list_format(obj, latest):
    """Lists all your data formats"""
    user, catalog = obj['config']['user'], obj['catalog']
    dfs = catalog.list_formats(latest, user=user)

    def format_record(df):
        return (df["name"], df["version"],
                util.format_description(df["description"]),
                util.get_status_string(df), df["modified"])

    dfs = [ format_record(df) for df in dfs ]

    click.echo("")
    click.echo("Data formats for {0}".format(user))
    click.echo(create_table(('Name', 'Version', 'Description', 'Status', 'Modified'), dfs))


@data_format.command()
@click.argument('data-format', metavar="name:version")
@click.pass_obj
def show(obj, data_format):
    '''Provides more information about FORMAT'''
    name, ver = parse_input(data_format)
    spec = obj['catalog'].get_format_spec(name, ver)

    click.echo(util.format_json(spec))


@data_format.command()
@click.argument('data-format')
@click.pass_obj
def publish(obj, data_format):
    """Publishes data format to make publicly available"""
    name, version = parse_input(data_format)
    user, catalog = obj['config']['user'], obj['catalog']

    if catalog.publish_format(user, name, version):
        click.echo("Data format has been published")
    else:
        click.echo("Data format could not be published")
