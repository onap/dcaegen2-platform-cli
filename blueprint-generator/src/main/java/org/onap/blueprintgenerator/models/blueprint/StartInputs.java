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

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.Getter; import lombok.Setter;

@Getter @Setter
@JsonInclude(value=Include.NON_NULL)
public class StartInputs {
	//private ArrayList<String> ports;
	private GetInput envs;

	public TreeMap<String, LinkedHashMap<String, Object>> createOnapStartInputs(TreeMap<String, LinkedHashMap<String, Object>> inps, ComponentSpec cs){
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		retInputs = inps;
		LinkedHashMap<String, Object> stringType  = new LinkedHashMap<String, Object>();

//		ArrayList<String> port = new ArrayList<String>();
//		String external = "";
//		if(cs.getAuxilary().getPorts() != null) {
//			for(String s: cs.getAuxilary().getPorts()) {
//				//create the ports
//				String portNumber = "";
//				StringBuffer buf = new StringBuffer();
//				for(int i = 0; i < s.length(); i++) {
//					if(!(s.charAt(i) == ':')) {
//						buf.append(s.charAt(i));
//					}
//					else {
//						external = s.replace(buf.toString() + ":", "");
//						break;
//					}
//				}
//				portNumber = buf.toString();
//				String p = "concat: [" + '"' + portNumber + ":" + '"' +", {get_input: external_port }]";
//				port.add(p);
//			}
//		}
//		this.setPorts(port);
//		//add the external port input
//		if(cs.getAuxilary().getPorts() != null) {
//			stringType.put("type", "string");
//			stringType.put("description", "Kubernetes node port on which collector is exposed");
//			stringType.put("default", "'" + external + "'") ;
//			retInputs.put("external_port", stringType);
//		}

		//set the envs
		GetInput env = new GetInput();
		env.setGet_input("envs");
		this.setEnvs(env);
		LinkedHashMap<String, Object> eMap = new LinkedHashMap();
		eMap.put("default", "{}");
		retInputs.put("envs", eMap);

		return retInputs;
	}
}
