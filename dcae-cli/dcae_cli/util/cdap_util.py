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
Provides utilities for cdap components
"""
import logging
import json
import requests
import six

from dcae_cli.util.logger import get_logger
from dcae_cli.util.exc import DcaeException
from dcae_cli.util import discovery

_logger = get_logger('cdap-utils')
_logger.setLevel(logging.DEBUG)

#HELPER FUNCTIONS
def _merge_spec_config_into_broker_put(jar, config, spec, params, templated_conf):
    """
    The purpose of this function is to form the CDAP Broker PUT from the CDAP compponent jar, spec, config, and params, where:
        - jar is a URL
        - config is the CDAP "auxillary file"
        - spec is the CDAP component specification
        - params contains the subkeys "app_config", "app_preferences", "program_preferences" from the parameters config specification
           - (this last one isn't REALLY needed because it is a subset of "spec", but some preprocessing has already been done, specifically "normalize_cdap_params"

    The CDAP Broker API existed well before the component spec, so there is overlap with different naming.
    In the future, if this component spec becomes production and everyone follows it, 
      I will change the broker API to use the same keys so that this mapping becomes unneccessary.
    However, while this is still a moving project, I am simply going to do a horrible mapping here. 

    The CDAP broker PUT looks as follows:
        {
            "service_component_type" : ...,
            "jar_url" : ...,
            "artifact_name" : ...,
            "artifact_version" : ...,
            "app_config" : ...,
            "app_preferences" : ...,
            "program_preferences": ...,
            "programs": ...,
            "streamname" : ...,
            "namespace" : ...,
            "service_endpoints" : ...
        }    

    "So you cooked up a story and dropped the six of us into a *meat grinder*" - Arnold Schwarzenegger, Predator.
    
    #RE: Streams/consumes: this is used in the designer for validation but does not lead to anything in the CDAP developers configuration. 
    """

    #map services/provides into service_endpoints broker JSON
    services = spec["services"]["provides"] # is [] if empty
    se = []
    if services != []:
        for s in services:
            se.append({"service_name" : s["service_name"], "service_endpoint" : s["service_endpoint"], "endpoint_method" : s["verb"]})

    BrokerPut = {
        "cdap_application_type" : "program-flowlet", #TODO! Fix this once Hydrator apps is integrated into this CLI tool. 
        "service_component_type" : spec["self"]["component_type"],
        "jar_url" : jar,
        "artifact_version" : config["artifact_version"],
        "artifact_name" : config["artifact_name"],
        "artifact_version" : config["artifact_version"],
        "programs": config["programs"],
        "streamname" : config["streamname"],
        "services" : se,
    }
   
    Optionals = {v : config[v] for v in [i for i in ["namespace"] if i in config]}

    #not a fan of whatever is going on in update such that I can't return this in single line
    BrokerPut.update(Optionals)
    BrokerPut.update(params)

    # NOTE: app_config comes from params
    BrokerPut["app_config"]["services_calls"] = templated_conf["services_calls"]
    BrokerPut["app_config"]["streams_publishes"] = templated_conf["streams_publishes"]
    BrokerPut["app_config"]["streams_subscribes"] = templated_conf["streams_subscribes"]

    return BrokerPut

def _get_broker_url_from_profile(profile):
    """
    Gets the broker URL from profile
    """
    #Functions named so well you don't need docstrings. (C) tombo 2017
    res = requests.get("http://{0}:8500/v1/catalog/service/{1}".format(profile.consul_host, profile.cdap_broker)).json()
    return "http://{ip}:{port}".format(ip=res[0]["ServiceAddress"], port=res[0]["ServicePort"])

#PUBLIC 
def run_component(catalog, params, instance_name, profile, jar, config, spec, templated_conf):
    """
    Runs a CDAP Component
    
    By the time this function is called, the instance_name and instance_name:rel have already been pushed into consul by this parent function
    instance_name will be overwritten by the broker and the rels key will be used by the broker to call the CBS
    """
    broker_url = _get_broker_url_from_profile(profile)

    #register with the broker
    broker_put = _merge_spec_config_into_broker_put(jar, config, spec, params, templated_conf)
    
    #helps the component developer debug their spec if CDAP throws a 400
    _logger.info("Your (unbound, bound will be shown if deployment completes) app_config is being sent as")
    _logger.info(json.dumps(broker_put["app_config"]))

    _logger.info("Your app_preferences are being sent as")
    _logger.info(json.dumps(broker_put["app_preferences"]))

    _logger.info("Your program_preferences are being sent as")
    _logger.info(json.dumps(broker_put["program_preferences"]))

    response = requests.put("{brokerurl}/application/{appname}".format(brokerurl=broker_url, appname=instance_name),
                            json = broker_put, 
                            headers = {'content-type':'application/json'})
    
    deploy_success = False
    try: 
        response.raise_for_status() #bomb if not 2xx
        deploy_success = True
    except:
        #need this to raise a dirty status code for tests to work, so not just logging
        raise DcaeException("A Deployment Error Occured. Broker Response: {0}, Broker Response Text: {1}".format(response.status_code, response.text))

    if deploy_success:
        #TODO: not sure what this error handling looks like, should never happen that a deploy succeeds but this get fails
        #Get the cluster URL to tell the user to go check their application
        response = requests.get(broker_url)
        response.raise_for_status() #bomb if not 2xx
        cdap_cluster = response.json()["managed cdap url"]

        #Fetch the Application's AppConfig to show them what the bound config looks like:
        #TODO: This should be an endpoint in the broker. I filed an issue in the broker. For now, do the horrendous special character mapping here.
        #TODO: This only fetches AppConfig, add AppPreferences
        ns = "default" if "namespace" not in broker_put else broker_put["namespace"]
        mapped_appname = ''.join(e for e in instance_name if e.isalnum()) 
        r = requests.get("{0}/v3/namespaces/{1}/apps/{2}".format(cdap_cluster, ns, mapped_appname)).json()
        config = r["configuration"]

        _logger.info("Deployment Complete!")
        _logger.info("The CDAP cluster API is at {0}. The *GUI* Port is {1}. You may now go check your application there to confirm it is running correctly.".format(cdap_cluster, response.json()["cdap GUI port"]))
        _logger.info("Your instance name is: {0}. In CDAP, this will appear as: {1}".format(instance_name, mapped_appname))
        _logger.info("The bound Configuration for this application is: {0}".format(config))

        #TODO: Should we tell the user about metrics and healthcheck to try those too?

def normalize_cdap_params(spec):
    """
    The CDAP component specification includes some optional fields that the broker expects.
    This parses the specification, includes those fields if those are there, and sets the broker defaults otherwise
    """
    Params = {}
    p = spec["parameters"]
    #app preferences
    Params["app_preferences"] = {} if "app_preferences" not in p else {param["name"] : param["value"] for param in p["app_preferences"]}
    #app config
    Params["app_config"] = {} if "app_config" not in p else {param["name"] : param["value"] for param in p["app_config"]}
    #program preferences
    if "program_preferences" not in p:
        Params["program_preferences"] = []
    else:
        Params["program_preferences"] = []
        for tup in p["program_preferences"]:
            Params["program_preferences"].append({"program_id" : tup["program_id"], 
                                                  "program_type" : tup["program_type"], 
                                                  "program_pref" : {param["name"] : param["value"] for param in tup["program_pref"]}})
    return Params

def undeploy_component(profile, instance_name):
    """
    Undeploys  a CDAP Component, which in CDAP terms means stop and delete
    """
    broker_url = _get_broker_url_from_profile(profile) 

    #call the delete
    response = requests.delete("{brokerurl}/application/{appname}".format(brokerurl=broker_url, appname=instance_name))
    try: 
        response.raise_for_status() #bomb if not 2xx
        _logger.info("Undeploy complete.")
        return True
    except Exception as e:
        _logger.error("An undeploy Error Occured: {2}. Broker Response: {0}, Broker Response Text: {1}".format(response.status_code, response.text, e))
        return False

