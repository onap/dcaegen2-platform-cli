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

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.blueprint.Blueprint;
import org.onap.blueprintgenerator.models.blueprint.Imports;
import org.onap.blueprintgenerator.models.blueprint.Node;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.Getter; import lombok.Setter;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;


@Getter @Setter
@JsonInclude(value=Include.NON_NULL)

public class OnapBlueprint extends Blueprint{
	public Blueprint createOnapBlueprint(ComponentSpec cs, String importPath, String override) {

		//create the inputs that will be used
		TreeMap<String, LinkedHashMap<String, Object>> inputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		//set the tosca definition which is the same for everything
		this.setTosca_definitions_version("cloudify_dsl_1_3");

		//set the imports 
		if(importPath != "") {
			Imports imps = new Imports();
			this.setImports(imps.createImportsFromFile(importPath));
		}
		else {
			Imports imps = new Imports();
			this.setImports(imps.createOnapImports());
		}

		//create the node template
		TreeMap<String, Node> nodeTemplate = new TreeMap<String, Node>();
		String nodeName = cs.getSelf().getName();

		//create the onap node that will be used
		OnapNode node = new OnapNode();
		inputs = node.createOnapNode(inputs, cs, override);
		nodeTemplate.put(nodeName, node);
		this.setNode_templates(nodeTemplate);

		//set the inputs
		this.setInputs(inputs);

		Blueprint bp = new Blueprint();
		bp.setImports(this.getImports());
		bp.setInputs(this.getInputs());
		bp.setNode_templates(this.getNode_templates());
		bp.setTosca_definitions_version(this.getTosca_definitions_version());

		return bp;

	}
}