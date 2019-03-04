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

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.Getter; import lombok.Setter;
@Getter @Setter
@JsonInclude(value=Include.NON_NULL)
public class Start {
	private StartInputs inputs;
	private LinkedHashMap<String, Object> envs;
	
	public TreeMap<String, LinkedHashMap<String, Object>> createOnapStart(TreeMap<String, LinkedHashMap<String, Object>> inps, ComponentSpec cs) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = inps;
		retInputs = inps;
		
		//create the start inputs
		StartInputs inputs = new StartInputs();
		inputs.createOnapStartInputs(retInputs, cs);
		this.setInputs(inputs);
		
		return retInputs;
	}
}
