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

package org.onap.blueprintgenerator.models.onapbp;

import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.blueprint.Interfaces;
import org.onap.blueprintgenerator.models.blueprint.Node;
import org.onap.blueprintgenerator.models.blueprint.Properties;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter; import lombok.Setter;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

@JsonIgnoreProperties(ignoreUnknown = true)
@Getter @Setter
@EqualsAndHashCode(callSuper=false)
@NoArgsConstructor
@JsonInclude(value=Include.NON_NULL)

public class OnapNode extends Node{
	private TreeMap<String, Interfaces> interfaces;
	private Properties properties;
	public TreeMap<String, LinkedHashMap<String, Object>> createOnapNode(TreeMap<String, LinkedHashMap<String, Object>> inps, ComponentSpec cs, String override) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		retInputs = inps;

		//create and set the interfaces
		Interfaces inter = new Interfaces();
		retInputs = inter.createInterface(retInputs, cs);
		TreeMap<String, Interfaces> interfaces = new TreeMap<String, Interfaces>();
		interfaces.put("cloudify.interfaces.lifecycle", inter);
		this.setInterfaces(interfaces);

		//set the type
		this.setType("dcae.nodes.ContainerizedPlatformComponent");

		//set the properties
		Properties props = new Properties();
		retInputs = props.createOnapProperties(retInputs, cs, override);
		this.setProperties(props);

		return retInputs;
	}
}