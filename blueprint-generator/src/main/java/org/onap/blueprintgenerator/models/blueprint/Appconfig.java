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

import org.onap.blueprintgenerator.models.componentspec.CallsObj;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.Parameters;
import org.onap.blueprintgenerator.models.componentspec.Publishes;
import org.onap.blueprintgenerator.models.componentspec.Subscribes;

import com.fasterxml.jackson.annotation.JsonAnyGetter;


import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class Appconfig {
	private CallsObj[] service_calls;
	private TreeMap<String, DmaapObj> stream_publishes;
	private TreeMap<String, DmaapObj> stream_subcribes;
	private TreeMap<String, Object> params;

	@JsonAnyGetter
	public TreeMap<String, Object> getParams(){
		return params;
	}

	public TreeMap<String, LinkedHashMap<String, Object>> createOnapAppconfig(TreeMap<String, LinkedHashMap<String, Object>> inps, ComponentSpec cs) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		retInputs = inps;

		//set service calls
		CallsObj[] call = new CallsObj[0];
		this.setService_calls(call);

		//set the stream publishes
		TreeMap<String, DmaapObj> streamPublishes = new TreeMap<String, DmaapObj>();

		if(cs.getStreams().getPublishes().length != 0) {
			for(Publishes p: cs.getStreams().getPublishes()) {
				if(p.getType().equals("data_router") || p.getType().equals("data router")) {
					//in this case the data router information gets added to the params so for now leave it alone
					String config = p.getConfig_key();
					DmaapObj pub = new DmaapObj();
					retInputs = pub.createOnapDmaapDRObj(retInputs, config, 'p');
					pub.setType(p.getType());
					streamPublishes.put(config, pub);
				} else if(p.getType().equals("message_router") || p.getType().equals("message router")) {
					String config = p.getConfig_key();
					DmaapObj pub = new DmaapObj();
					retInputs = pub.createOnapDmaapMRObj(retInputs, config, 'p');
					pub.setType(p.getType());
					streamPublishes.put(config, pub);
				}
			}
		}

		//set the stream publishes
		TreeMap<String, DmaapObj> streamSubscribes = new TreeMap<String, DmaapObj>();

		if(cs.getStreams().getSubscribes().length != 0) {
			for(Subscribes s: cs.getStreams().getSubscribes()) {
				if(s.getType().equals("data_router") || s.getType().equals("data router")) {
					//in this case the data router information gets added to the params so for now leave it alone
					String config = s.getConfig_key();
					DmaapObj sub = new DmaapObj();
					retInputs = sub.createOnapDmaapDRObj(retInputs, config, 'p');
					sub.setType(s.getType());
					streamSubscribes.put(config, sub);
				} else if(s.getType().equals("message_router") || s.getType().equals("message router")) {
					String config = s.getConfig_key();
					DmaapObj sub = new DmaapObj();
					retInputs = sub.createOnapDmaapMRObj(retInputs, config, 's');
					sub.setType(s.getType());
					streamSubscribes.put(config, sub);
				}
			}
		}

		this.setStream_publishes(streamPublishes);
		this.setStream_subcribes(streamSubscribes);

		//set the parameters into the appconfig
		TreeMap<String, Object> parameters = new TreeMap<String, Object>();
		for(Parameters p: cs.getParameters()) {
			String pName = p.getName();
			if(p.isSourced_at_deployment()) {
				GetInput paramInput = new GetInput();
				paramInput.setGet_input(pName);
				parameters.put(pName, paramInput);

				if(!p.getValue().equals("")) {
					LinkedHashMap<String, Object> inputs = new LinkedHashMap<String, Object>();
					inputs.put("type", "string");
					inputs.put("default", p.getValue());
					retInputs.put(pName, inputs);
				} else {
					LinkedHashMap<String, Object> inputs = new LinkedHashMap<String, Object>();
					inputs.put("type", "string");
					retInputs.put(pName, inputs);
				}
			} else {
				if(p.getType() == "string") {
					String val  =(String) p.getValue();
					val = '"' + val + '"';
					parameters.put(pName, val);
				}
				else {
					parameters.put(pName, p.getValue());
				}
				
			}
		}
		this.setParams(parameters);
		return retInputs;
	}

//	public void createTemplateAppconfig() {
//		//set service calls
//		CallsObj[] call = new CallsObj[0];
//		this.setService_calls(call);
//
//		//set the stream publishes
//		TreeMap<String, DmaapObj> streamPublishes = new TreeMap<String, DmaapObj>();
//		this.setStream_publishes(streamPublishes);
//		
//		//set the stream subscribes
//		TreeMap<String, DmaapObj> streamSubscribes = new TreeMap<String, DmaapObj>();
//		this.setStream_subcribes(streamSubscribes);
//	}
}
