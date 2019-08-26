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

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.blueprint.Node;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.Parameters;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.JsonGenerationException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator;

import lombok.Getter;
import lombok.Setter;

@Getter @Setter
@JsonInclude(JsonInclude.Include.NON_NULL)

public class PolicyModel {
	
	private String tosca_definition_version;
	private TreeMap<String, PolicyModelNode> node_types;
	private TreeMap<String, PolicyModelNode> data_types;
	
	public ArrayList<PolicyModel> createPolicyModels(ComponentSpec cs, String filePath) {
		ArrayList<PolicyModel> models = new ArrayList();
		Parameters[] params = cs.getParameters();
		
		ArrayList<String> groups = new ArrayList<String>();
		groups = getModelGroups(params);
		
		for(String s: groups) {
			PolicyModel model = new PolicyModel();
			model = model.createPolicyModel(s, params);
			//models.add(model);
			policyModelToYaml(filePath, model, s);
		}
		
//		for(PolicyModel p: models) {
//			policyModelToYaml(filePath, p);
//		}

		return models;
	}
	
	public ArrayList<String> getModelGroups(Parameters[] params) {
		ArrayList<String> groups = new ArrayList();
		
		for(Parameters p: params) {
			if(p.isPolicy_editable()) {
				if(groups.isEmpty()) {
					groups.add(p.getPolicy_group());
				} else {
					if(!groups.contains(p.getPolicy_group())) {
						groups.add(p.getPolicy_group());
					}
				}
			}
		}
		
		return groups;
	}
	
	public PolicyModel createPolicyModel(String s, Parameters[] params) {
		PolicyModel model = new PolicyModel();
		model.setTosca_definition_version("tosca_simple_yaml_1_0_0");
		
		PolicyModelNode node = new PolicyModelNode();
		String hasEntryScheme = node.createNodeType(s, params);	
		String nodeTypeName = "onap.policy." + s;
		TreeMap<String, PolicyModelNode> nodeType = new TreeMap();
		nodeType.put(nodeTypeName, node);
		model.setNode_types(nodeType);
		
		if(!hasEntryScheme.equals("")) {
			PolicyModelNode data = new PolicyModelNode();
			TreeMap<String, PolicyModelNode> dataType = data.createDataTypes(hasEntryScheme, params);
			model.setData_types(dataType);
		}
		
		return model;
	}
	
	public void policyModelToYaml(String path, PolicyModel p, String name) {
			File outputFile;
			String filePath = path + "/" + name + ".yml";
			File policyFile = new File(filePath);
			ObjectMapper policyMapper = new ObjectMapper(new YAMLFactory().configure(YAMLGenerator.Feature.MINIMIZE_QUOTES, true));
			outputFile = new File(path, name + ".yml");
			outputFile.getParentFile().mkdirs();

			try {
				PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(outputFile, true)));
			} catch (IOException e) {
				e.printStackTrace();
			}

			try {
				policyMapper.writeValue(outputFile, p);
			} catch (JsonGenerationException e) {
				e.printStackTrace();
			} catch (JsonMappingException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
			System.out.println("model " + name + " created");
	}
}
