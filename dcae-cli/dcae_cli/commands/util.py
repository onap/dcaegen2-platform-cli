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
Provides utilities for commands
"""
import json
import textwrap
from terminaltables import AsciiTable

from dcae_cli.util import DcaeException


def parse_input(input_):
    '''Returns (name, version) tuple parsed from name:version'''
    arg = input_.split(':')
    if len(arg) == 1:
        cname, cver = arg[0], None
    elif len(arg) == 2:
        cname, cver = arg
        cver = None if not cver else cver
    else:
        raise DcaeException("Input '{:}' must be NAME or NAME:VERSION".format(input_))
    return cname, cver


def parse_input_pair(req, resp):
    '''Returns a tuple output of `parse_input` for convenience'''
    return parse_input(req), parse_input(resp)


def create_table(header, entries):
    '''Returns an ASCII table string'''
    data = [header, ]
    if entries:
        data.extend(entries)
    else:
        data.append(['']*len(header))
    return AsciiTable(data).table


# Utility methods used to format records for displaying

def get_status_string(record):
    """Get the status label given a record of either data format or component"""
    if "when_revoked" not in record or "when_published" not in record or \
        "when_added" not in record:
        return None

    if record["when_revoked"] is not None:
        return "revoked"
    elif record["when_published"] is not None:
        return "published"
    else:
        return "staged"


def format_description(description, line_width=50, num_lines=3):
    """Formats the description field

    Description field can be long. This function line wraps to a specified number
    of lines. The last line trails with ".." if the text still overflows to
    signal that there is more.
    """
    lines = textwrap.wrap(description)
    lines = lines[:num_lines]
    last_line = lines.pop()

    if len(last_line) > line_width and line_width > 2:
        last_line = "{0}..".format(last_line[:-2])

    lines.append(last_line)
    return "\n".join(lines)


def format_json(some_json):
    return json.dumps(some_json, sort_keys=True, indent=4)
