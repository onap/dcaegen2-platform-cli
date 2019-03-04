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

import org.onap.blueprintgenerator.models.componentspec.Auxilary;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.HealthCheck;
import org.onap.blueprintgenerator.models.onapbp.OnapNode;

import lombok.Getter; import lombok.Setter;


public class TemplateNode extends OnapNode{
	
//	public void createTemplateNode() {
//		//dummy inputs just used for the inputs so i can reuse code
//		TreeMap<String, LinkedHashMap<String, Object>> inps = new TreeMap<String, LinkedHashMap<String, Object>>();
//		
//		//create a dummy componentspec to set the values later on 
//		ComponentSpec cs = new ComponentSpec();
//		Auxilary aux = new Auxilary();
//		HealthCheck health = new HealthCheck();
//		health.setEndpoint("/healthcheck");
//		health.setInterval("15s");
//		health.setTimeout("1s");
//		health.setType("https");
//		aux.setHealthcheck(health);
//		String[] ports = new String[1];
//		ports[0] = "9999:9999";
//		aux.setPorts(ports);
//		cs.setAuxilary(aux);
//		
//		//set the type
//		this.setType("dcae.nodes.ContainerizedPlatformComponent");
//		
//		//set the interface
//		Interfaces inter = new Interfaces();
//		inter.createOnapInterface(inps, cs);
//		TreeMap<String, Interfaces> interfaces = new TreeMap<String, Interfaces>();
//		interfaces.put("cloudify.interfaces.lifecycle", inter);
//		this.setInterfaces(interfaces);
//		
//		
//		//create the properties
//		Properties props = new Properties();
//		props.createTemplateProperties(cs);
//		this.setProperties(props);
//	}
}
