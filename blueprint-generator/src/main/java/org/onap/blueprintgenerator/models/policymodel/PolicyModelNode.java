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

package org.onap.blueprintgenerator.models.policymodel;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.blueprint.Node;
import org.onap.blueprintgenerator.models.componentspec.EntrySchemaObj;
import org.onap.blueprintgenerator.models.componentspec.Parameters;
import org.onap.blueprintgenerator.models.componentspec.PolicySchemaObj;

import com.fasterxml.jackson.annotation.JsonInclude;

import lombok.Getter;
import lombok.Setter;

@Getter @Setter
@JsonInclude(JsonInclude.Include.NON_NULL)
public class PolicyModelNode {
	
	private String derived_from;
	private TreeMap<String, PolicyProperties> properties;
	
	public String createNodeType(String policyName, Parameters[] params) {
		String hasEntrySchema = "";
		
		TreeMap<String, PolicyProperties> props = new TreeMap();
		for(Parameters p: params) {
			if(p.getPolicy_group() != null) {
				if(p.getPolicy_group().equals(policyName)) {
					String name = p.getName();
					String type = p.getType();
					PolicyProperties polProps = new PolicyProperties();
					if(p.getPolicy_schema() != null) {
						polProps.setType("map");
						HashMap<String, String> entrySchema = new HashMap();
						entrySchema.put("type", "onap.datatypes." + name);
						//ArrayList<String> entrySchema = new ArrayList<String>();
						//entrySchema.add("type: onap.data." + name);
						polProps.setEntry_schema(entrySchema);
						hasEntrySchema = name;
						props.put(name, polProps);
					}
					else {
						polProps.setType(type);
						props.put(name, polProps);
					}
				}
			}
		}
		
		this.setDerived_from("tosca.datatypes.Root");
		this.setProperties(props);
		return hasEntrySchema;
	}
	
	public TreeMap<String, PolicyModelNode> createDataTypes(String param, Parameters[] parameters) {
		TreeMap<String, PolicyModelNode> dataType = new TreeMap<String, PolicyModelNode>();
		
		PolicyModelNode node = new PolicyModelNode();
		node.setDerived_from("tosca.datatypes.Root");
		
		TreeMap<String, PolicyProperties> properties = new TreeMap();
		
		Parameters par = new Parameters();
		for(Parameters p: parameters) {
			if(p.getName().equals(param)) {
				par = p;
				break;
			}
		}
		
		for(PolicySchemaObj pol: par.getPolicy_schema()) {
			if(pol.getEntry_schema() != null) {
				PolicyProperties prop = new PolicyProperties();
				prop.setType("map");
				HashMap<String, String> schema = new HashMap();
				schema.put("type", "onap.datatypes." + pol.getName());
//				prop.setType("list");
//				ArrayList<String> schema = new ArrayList();
//				schema.add("type: onap.data." + pol.getName());
				prop.setEntry_schema(schema);
				properties.put(pol.getName(), prop);
				dataType = translateEntrySchema(dataType, pol.getEntry_schema(), pol.getName());
			}
			else {
				PolicyProperties prop = new PolicyProperties();
				prop.setType(pol.getType());
				properties.put(pol.getName(), prop);
			}
		}
		
		node.setProperties(properties);
		dataType.put("onap.datatypes." + param, node);
		return dataType;
	}
	
	private TreeMap<String, PolicyModelNode> translateEntrySchema(TreeMap<String, PolicyModelNode> dataType, EntrySchemaObj[] entry, String name){
		TreeMap<String, PolicyModelNode> data = dataType;
		PolicyModelNode node = new PolicyModelNode();
		node.setDerived_from("tosca.nodes.Root");
		TreeMap<String, PolicyProperties> properties = new TreeMap<String, PolicyProperties>();
		
		for(EntrySchemaObj e: entry) {
			if(e.getEntry_schema() != null) {
				PolicyProperties prop = new PolicyProperties();
				prop.setType("list");
				ArrayList<String> schema = new ArrayList<String>();
				schema.add("type: onap.datatypes." + e.getName());
				prop.setEntry_schema(schema);
				properties.put(e.getName(), prop);
				data = translateEntrySchema(data, e.getEntry_schema(), e.getName());
				node.setProperties(properties);
			} else {
				PolicyProperties prop = new PolicyProperties();
				prop.setType(e.getType());
				properties.put(e.getName(), prop);
				node.setProperties(properties);
			}
		}
		
		dataType.put("onap.datatypes." + name, node);
		return data;
	}

}
