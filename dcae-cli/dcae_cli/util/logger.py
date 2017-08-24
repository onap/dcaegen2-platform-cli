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
Provides logger utilities
"""
import logging

import click


class ClickHandler(logging.StreamHandler):

    def emit(self, record):
        msg = self.format(record)
        click.echo(msg)


_clihandler = ClickHandler()
_formatter = logging.Formatter('%(name)s | %(levelname)s | %(message)s')
_clihandler.setFormatter(_formatter)

_root = logging.getLogger('DCAE')
_root.setLevel(logging.WARNING)
_root.handlers = [_clihandler, ]
_root.propagate = False


def get_logger(name=None):
    return _root if name is None else _root.getChild(name)


def set_verbose():
    _root.setLevel(logging.INFO)


def set_quiet():
    _root.setLevel(logging.WARNING)
