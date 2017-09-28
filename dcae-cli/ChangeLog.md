# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## []

* Make server url (url to webserver that has static artifacts like json schemas) a configuration parameter
* Seeding configuration is no longer a fatal issue
* Setup database connection via manual user inputs if seed config not there
* Seeding profiles is no longer a fatal issue
* Dynamically fetch Docker login credentials from Consul to use to authenticate when creating Docker client.

## [2.9.0]

* Add data format generate command
* Fix issue with data router config keys

## [2.8.1]

* Improve error message when inputs map is missing item. Show the specific parameters that are causing issues.

## [2.8.0]

* Enhance to support parameters that are sourced at deployment
* Provide new command line arg --inputs-file
* Use inputs file to bind values to generated configuration for parameters that have been specified to be `sourced_at_deployment` true.

## [2.7.0]

* Rip out Docker related code and use common python-dockering library
    - Using 1.2.0 of python-dockering supports Docker exec based health checks
* Add support for volumes
* Add support for special DNS configuration in Docker containers to enable use of Consul DNS interface

## [2.6.0]

* Use port mappings from component spec when running Docker containers

## [2.5.0]

* Define the data structure for the input dmaap map items for data router that are passed in `--dmaap-file`. Enhance the json schema.
* Create the appropriate delivery url
* Enhance spec validation for cdap. Throw error when cdap specs have data router subscribes.
* Verify container is up in order to construct and to display data router subscriber delivery urls

## [2.4.0]

* Define the data structure for the input dmaap map items that are passed in `--dmaap-file`. Create and use json schema for validation and applying defaults.
* Group config keys by `streams_publishes`, `streams_subscribes`, and `services_calls` in generating the application config for both Docker and CDAP

## [2.3.2]

* Fix issue where components with dashes can't be found when running components that depend upon them. This one addressed the issue in the catalog and in the config creation part of discovery.
* Fix misleading "missing downstream component" warning that should be an error.

## [2.3.1]

* Fix issue where components with dashes can't be found when running components that depend upon them.
EDIT: This one addressed the issue in the catalog

## [2.3.0]

* Enhance the `component dev` command to print all the environment variables needed to work with the platform for development
* Display the component type in the `catalog list` view

## [2.2.0]

* Add fields `cli_version` and `schema_path` to both the components and data formats tables to be used as metadata which can be used for debugging.

## [2.1.0]

* (Re)Initialize both config and profiles by first grabbing files from Nexus
* Change `--reinit` to be eager and to be used to reinit config and profiles
* Remove *default* profile
* Replace the use of backports.tempfile with a combo of pytest `tmpdir` and `monkeypatch`

## [2.0.0]

* Update sqlalchemy and catalog to support postgres and remove mysql support. Still compatible with sqlite.
* Add the `catalog` command used to tap into the shared catalog
* Change the `component` and the `data_format` command to be for the particular user of the dcae-cli
* Changes to support component spec v3: folding of the auxilary specs into the component spec and adding of the property artifacts
* Add the ability to publish components and data formats

## [1.6.0]

* Enhance `component run` to take in dmaap json using the `--dmaap-file` option. This is used to generate configuration that will provide client-side dmaap configuration.

## [1.5.0]

* Enhance `component dev` to take in dmaap json using the `--dmaap-file` option. This is used to generate configuration that will provide client-side dmaap configuration.
* Make json schema remote file paths configurable.

## [1.4.0]

* Enhance component list view to show running instances. The standard view shows number of deployments associated with a component and an expanded view that show details of those deployments.

## [1.3.0]

* Fix queries to find unhealthy and defective instances to force dashes to be dots to ensure proper matching

## [1.2.0]

* Expand the undeploy command to include undeploying defective instances
* Remove suffix from name to fix mis-naming

## [0.12.0]

* Go back to setting of uid, expose setting of db url
* Add ability to *reinit* configuration via `--reinit`

## [0.11.0]

* Make CDAP Paramaters follow parameters definitions 
