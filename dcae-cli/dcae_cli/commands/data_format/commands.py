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

import genson

import sys

import os

from jsonschema import Draft4Validator

from dcae_cli.util import load_json
from dcae_cli.util.logger import get_logger

from dcae_cli.commands import util
from dcae_cli.commands.util import create_table, parse_input

from dcae_cli.catalog.exc import MissingEntry
from dcae_cli.catalog.exc import DcaeException


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

@data_format.command()
@click.option('--keywords', is_flag=True, help='Adds a template of possible descriptive keywords', default=False)
@click.argument('name_version', metavar="name:version",  required = True)
@click.argument('file-or-dir-path', type=click.Path(resolve_path=True, exists=True, dir_okay=True, file_okay=True, readable=True),   metavar="file-or-dir-path")
@click.pass_obj
def generate(obj, name_version, file_or_dir_path, keywords):
    '''Create schema from a file or directory examples'''
    name, version = parse_input(name_version)
    if version == None: 
      version = ""
    schema = genson.Schema()
    if os.path.isfile(file_or_dir_path):
      addfile(file_or_dir_path, schema)
    else:
      foundJSON = False
      for root, dirs, files in os.walk(file_or_dir_path):
          for filename in files:
            fullfilename = os.path.join(file_or_dir_path, filename)
            addfile(fullfilename,schema)
            foundJSON = True
      if foundJSON == False:
        raise DcaeException('No JSON files found in ' + file_or_dir_path)

    json_obj = json.loads(schema.to_json())
    json_obj['$schema'] = "http://json-schema.org/draft-04/schema#"
    jschema = json.dumps(json_obj)
    jschema = jschema.replace('"required":', '"additionalproperties": true, "required":')
    jschema = jschema.replace('"type":', ' "description": "", "type":')

    if (keywords):
      jschema = jschema.replace('"type": "string"', ' "maxLength": 0, "minLength": 0, "pattern": "", "type": "string"')
      jschema = jschema.replace('"type": "integer"', ' "maximum": 0, "mininimum": 0, "multipleOf": 0, "type": "integer"')
      jschema = jschema.replace('"type": "array"', ' "maxItems": 0, "minItems": 0, "uniqueItems": "false", "type": "array"')

    jschema = '{ "self": { "name": "' + name + '", "version": "' + version + '", "description": ""} , "dataformatversion": "1.0.0", "jsonschema": ' + jschema + '}'
    #Draft4Validator.check_schema(json.loads(jschema))
    try:
      print(json.dumps(json.loads(jschema), sort_keys=True, indent=4 ))
    except ValueError:
      raise DcaeException('Problem with JSON generation')

def addfile(filename, schema):
  try: 
    fileadd = open(filename, "r")
  except IOError:
    raise DcaeException('Cannot open' + filename)
  try: 
    json_object = json.loads(fileadd.read())
    schema.add_object(json_object)
  except ValueError:
    raise DcaeException('Bad JSON file: ' + filename)
  finally:
    fileadd.close()


