# ============LICENSE_START=======================================================
# org.onap.dcae
# ================================================================================
# Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
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
Function for Policy schema validation
"""

from jsonschema import validate, ValidationError
from dcae_cli.util.logger import get_logger
from dcae_cli.util import reraise_with_msg

logger = get_logger('policy')

_SCHEMA = {
  "$schema": "http://json-schema.org/draft-04/schema#",
  "title": "Schema for policy changes",
  "type": "object",
  "properties": {
      "updated_policies": {"type": "array"},
      "removed_policies": {"type": "array"},
      "policies":         {"type": "array"}
  },
  "additionalProperties": False
}

_validation_msg = """
Is your Policy file a valid json?
Does your Policy file follow this format?

{
  "updated_policies": [{},{},...],
  "removed_policies": [{},{},...],
  "policies":         [{},{},...]
}
"""


def validate_against_policy_schema(policy_file):
    """Validate the policy file against the schema"""

    try:
        validate(policy_file, _SCHEMA)
    except ValidationError as e:
        logger.error("Policy file validation issue")
        logger.error(_validation_msg)
        reraise_with_msg(e, as_dcae=True)
        