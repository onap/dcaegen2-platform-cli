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

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.blueprint.GetInput;
import org.onap.blueprintgenerator.models.blueprint.Interfaces;
import org.onap.blueprintgenerator.models.blueprint.Node;
import org.onap.blueprintgenerator.models.blueprint.Properties;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.Publishes;
import org.onap.blueprintgenerator.models.componentspec.Subscribes;
import org.onap.blueprintgenerator.models.onapbp.OnapNode;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@JsonIgnoreProperties(ignoreUnknown = true)
@Getter @Setter
@EqualsAndHashCode(callSuper=false)
@NoArgsConstructor
@JsonInclude(value=Include.NON_NULL)

public class DmaapNode extends Node{

	private TreeMap<String, Interfaces> interfaces;
	private Properties properties;
	private ArrayList<LinkedHashMap<String, String>> relationships;

	public TreeMap<String, LinkedHashMap<String, Object>> createDmaapNode(ComponentSpec cs, TreeMap<String, LinkedHashMap<String, Object>> inps, String override) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = inps;

		//set the type
		this.setType("dcae.nodes.ContainerizedServiceComponentUsingDmaap");

		//create the interface
		Interfaces inter = new Interfaces();
		retInputs = inter.createInterface(retInputs, cs);
		TreeMap<String, Interfaces> interfaces = new TreeMap<String, Interfaces>();
		interfaces.put("cloudify.interfaces.lifecycle", inter);
		this.setInterfaces(interfaces);

		//create and set the relationships
		ArrayList<LinkedHashMap<String, String>> rets = new ArrayList();

		//go through the streams publishes
		int counter = 0;
		if(cs.getStreams().getPublishes() != null) {
			for(Publishes p: cs.getStreams().getPublishes()) {
				LinkedHashMap<String, String> pubRelations = new LinkedHashMap();
				if(p.getType().equals("message_router") || p.getType().equals("message router")) {
					pubRelations.put("type", "ccsdk.relationships.publish_events");
					pubRelations.put("target", "topic" + counter);
				} else if(p.getType().equals("data_router") || p.getType().equals("data router")) {
					pubRelations.put("type", "ccsdk.relationships.publish_files");
					pubRelations.put("target", "feed" + counter);
				}
				rets.add(pubRelations);
				counter++;
			}
		}
		//go through the stream subscribes
		if(cs.getStreams().getSubscribes() != null) {
			for(Subscribes s: cs.getStreams().getSubscribes()) {
				LinkedHashMap<String, String> subRelations = new LinkedHashMap();
				if(s.getType().equals("message_router") || s.getType().equals("message router")) {
					subRelations.put("type", "ccsdk.relationships.subscribe_to_events");
					subRelations.put("target", "topic" + counter);
				} else if(s.getType().equals("data_router") || s.getType().equals("data router")) {
					subRelations.put("type", "ccsdk.relationships.subscribe_to_files");
					subRelations.put("target", "feed" + counter);
				}
				rets.add(subRelations);
				counter++;
			}
		}
		
		this.setRelationships(rets);

		//create and set the properties
		Properties props = new Properties();
		retInputs = props.createDmaapProperties(retInputs, cs, override);
		this.setProperties(props);

		return retInputs;
	}
	public TreeMap<String, LinkedHashMap<String, Object>> createFeedNode(ComponentSpec cs, TreeMap<String, LinkedHashMap<String, Object>> inps, String name){
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = inps;
		LinkedHashMap<String, Object> stringType = new LinkedHashMap();
		stringType.put("type", "string");

		//set the type
		this.setType("ccsdk.nodes.Feed");

		//create and set the properties
		Properties props = new Properties();
		GetInput topicInput = new GetInput();
		topicInput.setGet_input(name + "_name");
		props.setFeed_name(topicInput);
		//props.setUseExisting(true);
		retInputs.put(name + "_name", stringType);
		this.setProperties(props);

		return retInputs;
	}

	public TreeMap<String, LinkedHashMap<String, Object>> createTopicNode(ComponentSpec cs, TreeMap<String, LinkedHashMap<String, Object>> inps, String name){
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = inps;
		LinkedHashMap<String, Object> stringType = new LinkedHashMap();
		stringType.put("type", "string");

		//set the type
		this.setType("ccsdk.nodes.Topic");

		//create and set the properties
		Properties props = new Properties();
		GetInput topicInput = new GetInput();
		topicInput.setGet_input(name + "_name");
		props.setTopic_name(topicInput);
		//props.setUseExisting(true);
		retInputs.put(name + "_name", stringType);
		this.setProperties(props);

		return retInputs;
	}
}
