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

package org.onap.blueprintgenerator.models.dmaapbp;

import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.blueprint.Appconfig;
import org.onap.blueprintgenerator.models.blueprint.GetInput;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.HealthCheck;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.Getter;
import lombok.Setter;

@Getter @Setter
@JsonInclude(value=Include.NON_NULL)
public class DmaapStreams {

	private String name;
	private GetInput location;
	private GetInput client_role;
	private String type;

	private GetInput username;
	private GetInput password;
	//private GetInput delivery_url;
	private String route;
	private String scheme;

	public TreeMap<String, LinkedHashMap<String, Object>> createStreams(TreeMap<String, LinkedHashMap<String, Object>> inps, ComponentSpec cs, String name, String type, String key, String route, char o){
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = inps;
		LinkedHashMap<String, Object> stringType = new LinkedHashMap();
		stringType.put("type", "string");

		//set the name
		this.setName(name);

		//set the type
		this.setType(type);

		//set the location
		GetInput location = new GetInput();
		location.setGet_input(key + "_" + name + "_location");
		retInputs.put(key + "_" + name + "_location", stringType);
		this.setLocation(location);

		//if its data router we need to add some more
		if(type.equals("data_router") || type.equals("data router")) {
			if(o == 's') {
				//set the username
				GetInput username = new GetInput();
				username.setGet_input(key + "_" + name + "_username");
				this.setUsername(username);
				retInputs.put(key + "_" + name + "_username", stringType);

				//set the password
				GetInput password = new GetInput();
				password.setGet_input(key + "_" + name + "_password");
				this.setPassword(password);
				retInputs.put(key + "_" + name + "_password", stringType);

				this.setRoute(route);
				this.setScheme("https");
			}

//			//set the delivery url
//			GetInput delivery = new GetInput();
//			delivery.setGet_input(name + "_delivery_url");
//			this.setDelivery_url(delivery);
//			retInputs.put(name + "delivery_url", stringType);

		} else {
			//set the client role
			GetInput client = new GetInput();
			client.setGet_input(key + "_" + name + "_client_role");
			this.setClient_role(client);
			retInputs.put(key + "_" + name + "_client_role", stringType);
		}
		return retInputs;
	}
}