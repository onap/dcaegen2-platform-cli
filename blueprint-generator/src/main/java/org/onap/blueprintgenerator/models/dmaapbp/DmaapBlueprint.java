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

import org.onap.blueprintgenerator.models.blueprint.Blueprint;
import org.onap.blueprintgenerator.models.blueprint.Imports;
import org.onap.blueprintgenerator.models.blueprint.Interfaces;
import org.onap.blueprintgenerator.models.blueprint.Node;
import org.onap.blueprintgenerator.models.blueprint.Properties;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.Publishes;
import org.onap.blueprintgenerator.models.componentspec.Subscribes;

public class DmaapBlueprint extends Blueprint{
	public Blueprint createDmaapBlueprint(ComponentSpec cs, String importPath, String override) {
		Blueprint bp = new Blueprint();

		//set tosca definition
		bp.setTosca_definitions_version("cloudify_dsl_1_3");

		//set the description
		bp.setDescription(cs.getSelf().getDescription());

		//create the inpus object that will be added to over the creation of the blueprint
		TreeMap<String, LinkedHashMap<String, Object>> inps = new TreeMap<String, LinkedHashMap<String, Object>>();

		//set the imports
		Imports imps = new Imports();
		if(importPath.equals("")) {
			bp.setImports(imps.createDmaapImports());
		}
		else {
			bp.setImports(imps.createImportsFromFile(importPath));
		}

		//bp.setImports(imps.getImports());

		//set and create the node templates
		TreeMap<String, Node> nodeTemplate = new TreeMap();

		//create and add the main dmaap node
		DmaapNode dmaap = new DmaapNode();
		inps = dmaap.createDmaapNode(cs, inps, override);
		nodeTemplate.put(cs.getSelf().getName(), dmaap);

		//create and add the topic/feed nodes

		//go through the streams publishes
		int counter = 0;
		if(cs.getStreams().getPublishes() != null) {
			for(Publishes p: cs.getStreams().getPublishes()) {
				if(p.getType().equals("message_router") || p.getType().equals("message router")) {
					String topic = "topic" + counter;
					DmaapNode topicNode = new DmaapNode();
					inps = topicNode.createTopicNode(cs, inps, topic);
					nodeTemplate.put(topic, topicNode);
				} else if(p.getType().equals("data_router") || p.getType().equals("data router")) {
					String feed = "feed" + counter;
					DmaapNode feedNode = new DmaapNode();
					inps = feedNode.createFeedNode(cs, inps, feed);
					nodeTemplate.put(feed, feedNode);
				}
				counter++;
			}
		}
		//go through the stream subscribes
		if(cs.getStreams().getSubscribes() != null) {
			for(Subscribes s: cs.getStreams().getSubscribes()) {
				if(s.getType().equals("message_router") || s.getType().equals("message router")) {
					String topic = "topic" + counter;
					DmaapNode topicNode = new DmaapNode();
					inps = topicNode.createTopicNode(cs, inps, topic);
					nodeTemplate.put(topic, topicNode);
				} else if(s.getType().equals("data_router") || s.getType().equals("data router")) {
					String feed = "feed" + counter;
					DmaapNode feedNode = new DmaapNode();
					inps = feedNode.createFeedNode(cs, inps, feed);
					nodeTemplate.put(feed, feedNode);
				}
				counter++;
			}
		}

		bp.setNode_templates(nodeTemplate);

		bp.setInputs(inps);
		return bp;
	}
}