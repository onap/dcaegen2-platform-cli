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


import java.io.File;
import java.io.IOException;
import java.util.ArrayList;


import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator;
import lombok.AllArgsConstructor;
import lombok.Getter; import lombok.Setter;
import lombok.NoArgsConstructor;



@Getter @Setter
@JsonInclude(value=Include.NON_NULL)
public class Imports {
	/** The imports. */
	private ArrayList<String> imports;

	public static ArrayList<String> createOnapImports() {
		ArrayList<String> imps = new ArrayList<String>();
		imps.add("http://www.getcloudify.org/spec/cloudify/3.4/types.yaml");
		imps.add("https://nexus.onap.org/service/local/repositories/raw/content/org.onap.dcaegen2.platform.plugins/R4/k8splugin/1.4.5/k8splugin_types.yaml");
		imps.add("https://nexus.onap.org/service/local/repositories/raw/content/org.onap.dcaegen2.platform.plugins/R4/dcaepolicyplugin/2.3.0/dcaepolicyplugin_types.yaml");
		return imps;
	}
	public static ArrayList<String> createDmaapImports(){
		ArrayList<String> imps = new ArrayList<String>();
		imps.add("http://www.getcloudify.org/spec/cloudify/3.4/types.yaml");
		imps.add("https://nexus.onap.org/service/local/repositories/raw/content/org.onap.dcaegen2.platform.plugins/R5/k8splugin/1.6.0/k8splugin_types.yaml");
		imps.add("https://nexus.onap.org/service/local/repositories/raw/content/org.onap.ccsdk.platform.plugins/type_files/dmaap/dmaap.yaml");
		return imps;
	}
	public static ArrayList<String> createImportsFromFile(String path) {
		Imports imports = new Imports();
		ObjectMapper importMapper = new ObjectMapper(new YAMLFactory().configure(YAMLGenerator.Feature.MINIMIZE_QUOTES, true));
		File importPath = new File(path);
		try {
			imports = importMapper.readValue(importPath, Imports.class);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
		ArrayList<String> imps = new ArrayList<String>();
		for(String s: imports.getImports()) {
			imps.add(s);
		}
		return imps;
	}
}
