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
@JsonInclude(value=Include.NON_NULL)
@Getter @Setter
public class DmaapObj {
	private String dmaap_info;
	private String type;
	private GetInput pass;
	private GetInput user;

	public TreeMap<String, LinkedHashMap<String, Object>> createOnapDmaapMRObj(TreeMap<String, LinkedHashMap<String, Object>> inps, String config, char type, String n, String num) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		LinkedHashMap<String, Object> stringType = new LinkedHashMap();
		stringType.put("type", "string");
		retInputs = inps;

		//set the dmaapinfo
		DmaapInfo info = new DmaapInfo();
		String infoType = "<<" + n + ">>";
		this.setDmaap_info(infoType);

		//set username
		GetInput u = new GetInput();
		u.setGet_input(config + "_" + num +"_aaf_username");
		this.setUser(u);
		retInputs.put(config + "_" + num +"_aaf_username", stringType);

		//set password
		GetInput p = new GetInput();
		p.setGet_input(config + "_" + num +"_aaf_password");
		this.setPass(p);
		retInputs.put(config + "_" + num +"_aaf_password", stringType);

		return retInputs;
	}
	public TreeMap<String, LinkedHashMap<String, Object>> createOnapDmaapDRObj(TreeMap<String, LinkedHashMap<String, Object>> inps, String config, char type, String n, String num) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		retInputs = inps;
		
		//set the dmaapinfo
		DmaapInfo info = new DmaapInfo();
		String infoType = "<<" + n + ">>";
		this.setDmaap_info(infoType);
		return retInputs;
	}
}
