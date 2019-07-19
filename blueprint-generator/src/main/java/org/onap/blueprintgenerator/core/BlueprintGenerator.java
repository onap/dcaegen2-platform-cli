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

package org.onap.blueprintgenerator.core;



import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Options;
import org.onap.blueprintgenerator.models.blueprint.Blueprint;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;



@SuppressWarnings("deprecation")
public class BlueprintGenerator {

	private static String componentSpecPath = "";

	private static String bluePrintName = "";

	private static String outputPath = "";

	private static char bpType = 'o';

	private static String importPath = "";
	
	private static String override = "";


	public static void main(String[] args) throws Exception {

		printInstructions();

		parseInputs(args);

		//create the component Spec we are going to be working with
		ComponentSpec cs = new ComponentSpec();
		cs.createComponentSpecFromFile(componentSpecPath);

		//create the blueprint and convert it to a yaml file
		Blueprint bp = new Blueprint();
		bp = bp.createBlueprint(cs, bluePrintName, bpType, importPath, override);
		bp.blueprintToYaml(outputPath, bluePrintName, cs);
	}


	public static void printInstructions() {
		System.out.println("OPTIONS:");
		System.out.println("-i: The path to the JSON spec file (required)");
		System.out.println("-n: Name of the blueprint (optional)");
		System.out.println("-p: The path to the final blueprint (required)");
		System.out.println("-t: The path to the yaml import file (optional)");
		System.out.println("-d: With this flag present the blueprint will be created with the dmaap plugin enables");
		System.out.println("-o: The value you want for service_component_name_override (optional)");
	}

	public static void parseInputs(String[] args) throws Exception {
		//convert the arguments array to a string to make it easier
		String commands = "";
		for(String s: args) {
			if(commands.length() == 0) {
				commands = s;
			}
			else {
				commands = commands + " " + s;
			}
		}

		//check if it has the required inputs
		if(!commands.contains("-p") || !commands.contains("-i")) {
			System.out.println("did not enter the required inputs");
		}
		else {
			BasicParser parser = new BasicParser();
			Options options = new Options();
			options.addOption("i", "Spec", true, "ComponentSpec import file");
			options.addOption("p", "Path", true, "Path to the final blueprint");
			options.addOption("n", "Name", true, "Name of the blueprint");
			options.addOption("t", "imports", true, "Path to the import file");
			options.addOption("d", "Dmaap", false, "Enable the dmaap plugin");
			options.addOption("o", "Override", true, "service component name override");

			CommandLine commandLine = parser.parse(options, args);
			componentSpecPath = commandLine.getOptionValue("i");
			outputPath = commandLine.getOptionValue("p");
			override = commandLine.getOptionValue("o");
			if(!(commandLine.getOptionValue("n") == null)){
				bluePrintName = commandLine.getOptionValue("n");
			}
			if(!(commandLine.getOptionValue("t") == null)) {
				importPath = commandLine.getOptionValue("t");
			}
			if(commands.contains("-d")) {
				bpType = 'd';
			}
		}

	}
}

