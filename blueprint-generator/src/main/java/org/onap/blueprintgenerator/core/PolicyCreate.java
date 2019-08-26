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

import java.util.ArrayList;

import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Options;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.policymodel.PolicyModel;

public class PolicyCreate {

	private static String componentSpecPath = "";

	private static String outputPath = "";
	


	public static void main(String[] args) throws Exception {
		printInstructions();
		parseInputs(args);
		
		ComponentSpec cs = new ComponentSpec();
		cs.createComponentSpecFromFile(componentSpecPath);
		
		PolicyModel p = new PolicyModel();
		ArrayList<PolicyModel> models = p.createPolicyModels(cs, outputPath);
	}

	public static void printInstructions() {
		System.out.println("OPTIONS:");
		System.out.println("-i: The path to the JSON spec file (required)");
		System.out.println("-p: The output path for all of the models (required)");
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
			System.exit(0);
		}
		else {
			BasicParser parser = new BasicParser();
			Options options = new Options();
			options.addOption("i", "Spec", true, "ComponentSpec import file");
			options.addOption("p", "Path", true, "Path to the final blueprint");

			CommandLine commandLine = parser.parse(options, args);
			componentSpecPath = commandLine.getOptionValue("i");
			outputPath = commandLine.getOptionValue("p");

		}
	}	
}
