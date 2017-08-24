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

import pkg_resources

from docutils.nodes import literal_block
from sphinx.domains import Domain
from sphinx.util.compat import Directive

import click

from dcae_cli.cli import cli as group  # PYTHONPATH dynamically altered in conf.py


def generate_help_texts(command, prefix):
    ctx = click.Context(command)
    yield make_block(
        ' '.join(prefix),
        command.get_help_option(ctx).opts[0],
        command.get_help(ctx),
    )

    if isinstance(command, click.core.Group):
        for c in command.list_commands(ctx):
            c = command.resolve_command(ctx, [c])[1]
            prefix.append(c.name)
            for h in generate_help_texts(c, prefix):
                yield h
            prefix.pop()


def find_script_callable(name):
    return list(pkg_resources.iter_entry_points(
        'console_scripts', name))[0].load()


def make_block(command, opt, content):
    h = "$ {} {}\n".format(command, opt) + content
    return literal_block(h, h, language='bash')


class ClickHelpDirective(Directive):
    has_content = True
    required_arguments = 1

    def run(self):
        root_cmd = self.arguments[0]
        #group = find_script_callable(root_cmd)
        return list(generate_help_texts(group, [root_cmd]))


class DcaeCliDomain(Domain):
    name = 'dcae_cli'
    label = 'DCAE-CLI'
    directives = {
        'click-help': ClickHelpDirective,
    }


def setup(app):
    app.add_domain(DcaeCliDomain)
