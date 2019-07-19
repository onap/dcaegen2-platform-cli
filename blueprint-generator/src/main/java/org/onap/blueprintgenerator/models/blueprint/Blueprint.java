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

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.TreeMap;
import java.util.regex.Pattern;

import org.onap.blueprintgenerator.core.Fixes;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.Parameters;
import org.onap.blueprintgenerator.models.componentspec.Publishes;
import org.onap.blueprintgenerator.models.componentspec.Subscribes;
import org.onap.blueprintgenerator.models.dmaapbp.DmaapBlueprint;
import org.onap.blueprintgenerator.models.onapbp.OnapBlueprint;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.JsonProcessingException;
//import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;



@Getter @Setter
@JsonInclude(JsonInclude.Include.NON_NULL)

public class Blueprint {


	private String tosca_definitions_version;

	private String description;

	private ArrayList<String> imports;

	private TreeMap<String, LinkedHashMap<String, Object>> inputs;

	private TreeMap<String, Node> node_templates;

	public Blueprint createBlueprint(ComponentSpec cs, String name, char bpType, String importPath, String override) {
		Blueprint bp = new Blueprint();
		if(bpType == 'o') {
			OnapBlueprint onap = new OnapBlueprint();
			bp = onap.createOnapBlueprint(cs, importPath, override);
			bp = bp.setQuotations(bp);
		}

		if(bpType == 'd') {
			DmaapBlueprint dmaap = new DmaapBlueprint();
			bp = dmaap.createDmaapBlueprint(cs, importPath, override);
			bp = bp.setQuotations(bp);
		}
		return bp;
	}
	public Blueprint setQuotations(Blueprint bp) {
		for(String s: bp.getInputs().keySet()) {
			LinkedHashMap<String, Object> temp = bp.getInputs().get(s);
			if(temp.get("type") == "string") {
				String def = (String) temp.get("default");
				def = '"' + def + '"';
				temp.replace("default", def);
				bp.getInputs().replace(s, temp);
			}
		}
		
		return bp;
	}

	public void blueprintToYaml(String outputPath, String bluePrintName, ComponentSpec cs) {
		File outputFile;

		if(bluePrintName.equals("")) {
			String name = cs.getSelf().getName();
			if(name.contains(".")) {
				name = name.replaceAll(Pattern.quote("."), "_");
			}
			if(name.contains(" ")) {
				name = name.replaceAll(" ", "");
			}
			String file = name + ".yaml";


			outputFile = new File(outputPath, file);
			outputFile.getParentFile().mkdirs();
			try {
				outputFile.createNewFile();
			} catch (IOException e) {
				
				throw new RuntimeException(e);
			}
		} else {
			if(bluePrintName.contains(" ") || bluePrintName.contains(".")) {
				bluePrintName = bluePrintName.replaceAll(Pattern.quote("."), "_");
				bluePrintName = bluePrintName.replaceAll(" ", "");
			}
			String file = bluePrintName + ".yaml";
			outputFile = new File(outputPath, file);
			outputFile.getParentFile().mkdirs();
			try {
				outputFile.createNewFile();
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
		}

		String version = "#blueprint_version: " + cs.getSelf().getVersion() + '\n';
		String description = "#description: " + cs.getSelf().getDescription() + '\n';

		BufferedWriter writer = null;
		try {
			writer = new BufferedWriter(new FileWriter(outputFile, false));
		} catch (IOException e1) {
			throw new RuntimeException(e1);
		}
		if(writer != null) {
			try {
				writer.write(description);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			try {
				writer.write(version);
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
			try {
				writer.close();
			} catch (IOException e) {
				throw new RuntimeException(e);
			}
		}


		//read the translated blueprint into the file
		ObjectMapper blueprintMapper = new ObjectMapper(new YAMLFactory().configure(YAMLGenerator.Feature.MINIMIZE_QUOTES, true));

		PrintWriter out = null;
		try {
			out = new PrintWriter(new BufferedWriter(new FileWriter(outputFile, true)));
		} catch (IOException e) {
			throw new RuntimeException(e);
		}

		try {
			if(out != null) {
				blueprintMapper.writeValue(out, this);
				out.close();
			}
		} catch (IOException e) {
			
			throw new RuntimeException(e);
		}


		Fixes fix = new Fixes();
		try {
			fix.fixSingleQuotes(outputFile);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}

		System.out.println("Blueprint created");
	}


	public String blueprintToString() {
		String ret = "";

		ObjectMapper blueprintMapper = new ObjectMapper(new YAMLFactory().configure(YAMLGenerator.Feature.MINIMIZE_QUOTES, true));
		try {
			ret = blueprintMapper.writerWithDefaultPrettyPrinter().writeValueAsString(this);
		} catch (JsonProcessingException e) {
			throw new RuntimeException(e);
		}


		return ret;
	}
}
