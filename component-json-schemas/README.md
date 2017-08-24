# Component JSON Schemas

This repository contains the custom JSON schemas to support the onboarding of components:

* Component specification schema
* Auxilary component specification schema for Docker
* Auxilary component specification schema for CDAP
* Data formats schema

## Testing changes

Use the Python `jsonschema` command-line tool to do validation checks:

Example:

```
$ jsonschema -i tests/component-spec-docker.json component-spec-schema.json
```

## Uploading to Nexus

For the component specification schema:

```
curl -v --user <user>:<password> https://<your file server host>/schemas/component-specification/<tag>/component-spec-schema.json --upload-file component-spec-schema.json
```

For the data format schema:

```
curl -v --user <user>:<password> https://<your file server host>/schemas/data-format/<tag>/data-format-schema.json --upload-file data-format-schema.json
```

### `dcae-cli`

The `dcae-cli` looks for these schemas under a tag that is of the format `dcae-cli-v<major version>` where the major version is an integer that is the major part of semver.  For schema changes that are breaking, you must bump the `<major version>`.  Otherwise, you can simply replace the existing schema by uploading using the same tag.
