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

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;

public class Fixes {
	private static ArrayList<String> lines = new ArrayList<String>();
    private static String line = null;
	
    public static void fixSingleQuotes(File f) throws IOException {
		File translateFile = f;
		try {
			FileReader fr = new FileReader(translateFile);
			BufferedReader br = new BufferedReader(fr);
			while((line = br.readLine()) != null) {
				if(line.contains("'")) {
					line = line.replace("'", "");
				}
				if(line.contains("\"\"") && (line.contains("m") || line.contains("M"))) {
					line = line.replaceAll("\"\"", "\"");
				}
				lines.add(line);

			}
			fr.close();
			br.close();
			FileWriter fw = new FileWriter(translateFile);
			PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(f, true)));
			for(String s: lines) {
				out.println();
				out.write(s);
				out.flush();
			}
		
			out.close();
			fw.close();
			line = null;
			lines = new ArrayList<String>();
		} catch (FileNotFoundException e) {
			throw new RuntimeException(e);
		}
	}
}
