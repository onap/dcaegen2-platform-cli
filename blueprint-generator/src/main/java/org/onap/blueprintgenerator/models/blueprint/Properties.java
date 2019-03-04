/**============LICENSE_START======================================================= 
 org.onap.dcae 
 ================================================================================ 
 Copyright (c) 2019 AT&T Intellectual Property. All rights reserved. 
 ================================================================================ 
 Licensed under the Apache License, Version 2.0 (the "License"); 
 you may not use this file except in compliance with the License. 
 You may obtain a copy of the License at 

      http://www.apache.org/licenses/LICENSE-2.0 

 Unless required by applicable law or agreed to in writing, software 
 distributed under the License is distributed on an "AS IS" BASIS, 
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
 See the License for the specific language governing permissions and 
 limitations under the License. 
 ============LICENSE_END========================================================= 

 */

package org.onap.blueprintgenerator.models.blueprint;

import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.HealthCheck;
import org.onap.blueprintgenerator.models.componentspec.Volumes;
import org.onap.blueprintgenerator.models.onapbp.LogDirectory;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.Getter; import lombok.Setter;

@Getter @Setter
@JsonInclude(value=Include.NON_NULL)
public class Properties {
	private Appconfig application_config;
	private HealthCheck docker_config;
	private Object image;
	private GetInput log_info;
	private String dns_name;
	private Object replicas;
	private String name;

	public TreeMap<String, LinkedHashMap<String, Object>> createOnapProperties(TreeMap<String, LinkedHashMap<String, Object>> inps, ComponentSpec cs) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		retInputs = inps;

		//set the image
		GetInput image = new GetInput();
		image.setGet_input("tag_version");
		this.setImage(image);
		LinkedHashMap<String, Object> img = new LinkedHashMap<String, Object>();
		img.put("type", "string");
		img.put("default", cs.getArtifacts()[0].getUri());
		retInputs.put("tag_version", img);

		//set the log info
		GetInput logD = new GetInput();
		logD.setGet_input("log_directory");
		this.setLog_info(logD);
		String logger = "";
		for(Volumes v: cs.getAuxilary().getVolumes()) {
			if(v.getContainer().getBind().contains("/opt/app/") && v.getContainer().getBind().contains("logs")) {
				logger = v.getContainer().getBind();
			}
		}
		LinkedHashMap<String, Object> logInp = new LinkedHashMap<String, Object>();
		logInp.put("type", "string");
		if(logger != "") {
			logInp.put("default", logger);
		}
		retInputs.put("log_directory", logInp);
		
		//set the replicas
		GetInput replica = new GetInput();
		replica.setGet_input("replicas");
		this.setReplicas(replica);
		LinkedHashMap<String, Object> rep = new LinkedHashMap<String, Object>();
		rep.put("type", "integer");
		rep.put("description", "number of instances");
		rep.put("default", 1);
		retInputs.put("replicas", rep);

		//set the dns name
		this.setDns_name(cs.getSelf().getName());
		
		//set the name
		this.setName(cs.getSelf().getName());

		//set the docker config
		this.setDocker_config(cs.getAuxilary().getHealthcheck());

		//set the app config
		Appconfig app = new Appconfig();
		retInputs = app.createOnapAppconfig(retInputs, cs);
		this.setApplication_config(app);

		return retInputs;
	}

//	public void createTemplateProperties(ComponentSpec cs) {
//		//create dummy inputs just for methods
//		TreeMap<String, LinkedHashMap<String, Object>> inps = new TreeMap<String, LinkedHashMap<String, Object>>();
//		
//		//set the image
//		GetInput image = new GetInput();
//		image.setGet_input("tag_version");
//		this.setImage(image);
//		
//		//set the log info
//		LogDirectory log = new LogDirectory();
//		log.setLog_directory("Log directory");
//		this.setLog_info(log);
//
//		//set the replicas
//		GetInput replica = new GetInput();
//		replica.setGet_input("replicas");
//		this.setReplicas(replica);
//
//		//set the dns name
//		this.setDns_name("blueprint_template");
//		
//		//set the docker config
//		this.setDocker_config(cs.getAuxilary().getHealthcheck());
//		
//		//set the app config
//		Appconfig app = new Appconfig();
//		app.createTemplateAppconfig();
//		this.setApplication_config(app);
//	}

}
