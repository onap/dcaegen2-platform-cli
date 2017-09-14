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
Functions for handling inputs
"""

class InputsValidationError(RuntimeError):
    pass

def filter_entries(inputs_map, spec):
    """Filter inputs entries that are not in the spec"""
    param_names = [ p["name"] for p in spec["parameters"] \
            if "sourced_at_deployment" in p and p["sourced_at_deployment"] ]

    # Identify any missing parameters from inputs_map
    missing = list(filter(lambda pn: pn not in inputs_map, param_names))

    if missing:
        raise InputsValidationError(
            "Inputs map is missing keys: {0}".format(missing))

    return { pn: inputs_map[pn] for pn in param_names }
