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

package org.onap.blueprintgenerator.models.componentspec;

import java.io.File;
import java.io.IOException;
import java.util.Map;



import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.Getter; import lombok.Setter;
import lombok.NoArgsConstructor;

// TODO: Auto-generated Javadoc
/**
 * The Class ComponentSpec.
 */
@JsonIgnoreProperties(ignoreUnknown = true)

/* (non-Javadoc)
 * @see java.lang.Object#toString()
 */
@Getter @Setter

/* (non-Javadoc)
 * @see java.lang.Object#toString()
 */


/**
 * Instantiates a new component spec.
 */
@NoArgsConstructor

/**
 * Instantiates a new component spec.
 *
 * @param self the self
 * @param services the services
 * @param streams the streams
 * @param parameters the parameters
 * @param auxilary the auxilary
 * @param artifacts the artifacts
 */

@JsonInclude(value=Include.NON_NULL)
//main object that the component spec file is written in
public class ComponentSpec {
	
	/** The self. */
	private Self self; 
	
	/** The services. */
	private Services services;
	
	/** The streams. */
	private Streams streams;
	
	/** The parameters. */
	private Parameters[] parameters;
	
	/** The auxilary. */
	private Auxilary auxilary;
	
	/** The artifacts. */
	private Artifacts[] artifacts;

	/**
	 * Creates the component spec from file.
	 *
	 * @param path the path
	 */
	public void createComponentSpecFromFile(String path) {
		ObjectMapper componentMapper = new ObjectMapper();
		File specPathFile = new File(path);
		ComponentSpec cs = new ComponentSpec();

		try {
			cs = componentMapper.readValue(specPathFile, ComponentSpec.class);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}



		//set all the pieces of the component spec
		this.setSelf(cs.getSelf()); 
		this.setArtifacts(cs.getArtifacts());
		this.setAuxilary(cs.getAuxilary());
		this.setParameters(cs.getParameters());
		this.setServices(cs.getServices());
		this.setStreams(cs.getStreams());
	}


	/**
	 * Creates the component spec from string.
	 *
	 * @param specString the spec string
	 */
	public void createComponentSpecFromString(String specString) {
		ObjectMapper componentMapper = new ObjectMapper();
		ComponentSpec cs = new ComponentSpec();
		try {
			cs = componentMapper.readValue(specString, ComponentSpec.class);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}

		//set all the pieces of the component spec
		this.setSelf(cs.getSelf()); 
		this.setArtifacts(cs.getArtifacts());
		this.setAuxilary(cs.getAuxilary());
		this.setParameters(cs.getParameters());
		this.setServices(cs.getServices());
		this.setStreams(cs.getStreams());
	}


}
