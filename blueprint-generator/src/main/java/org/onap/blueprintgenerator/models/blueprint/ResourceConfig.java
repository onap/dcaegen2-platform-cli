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

import java.util.LinkedHashMap;
import java.util.TreeMap;

import com.fasterxml.jackson.annotation.JsonInclude;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

//TODO: Auto-generated Javadoc
/* (non-Javadoc)
* @see java.lang.Object#toString()
*/
@Getter @Setter

/* (non-Javadoc)
* @see java.lang.Object#toString()
*/
@Builder

/**
* Instantiates a new resource config obj.
*/
@NoArgsConstructor

/**
* Instantiates a new resource config obj.
*
* @param limits the limits
* @param requests the requests
*/
@AllArgsConstructor

public class ResourceConfig {

	/** The limits. */
	private TreeMap<String, GetInput> limits;

	/** The requests. */
	private TreeMap<String, GetInput> requests;


	/**
	 * Creates the resource config.
	 *
	 * @param inps the inps
	 * @param name the name
	 * @return the tree map
	 */
	public TreeMap<String, LinkedHashMap<String, Object>> createResourceConfig(TreeMap<String, LinkedHashMap<String, Object>> inps, String name){
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = inps;

		LinkedHashMap<String, Object> mi = new LinkedHashMap<String, Object>();
		mi.put("type", "string");
		mi.put("default", "128Mi");

		LinkedHashMap<String, Object> m = new LinkedHashMap<String, Object>();
		m.put("type", "string");
		m.put("default", "250m");


		if(!name.equals("")) {
			name = name + "_";
		}

		//set the limits
		TreeMap<String, GetInput> lim = new TreeMap<String, GetInput>();

		GetInput cpu = new GetInput();
		cpu.setGet_input(name + "cpu_limit");
		lim.put("cpu", cpu);

		GetInput memL = new GetInput();
		memL.setGet_input(name + "memory_limit");
		lim.put("memory", memL);

		retInputs.put(name + "cpu_limit", m);
		retInputs.put(name + "memory_limit", mi);

		this.setLimits(lim);

		//set the requests
		TreeMap<String, GetInput> req = new TreeMap<String, GetInput>();

		GetInput cpuR = new GetInput();
		cpuR.setGet_input(name + "cpu_request");
		req.put("cpu", cpuR);

		GetInput memR = new GetInput();
		memR.setGet_input(name + "memory_request");
		req.put("memory", memR);

		retInputs.put(name + "cpu_request", m);
		retInputs.put(name + "memory_request", mi);

		this.setRequests(req);

		return retInputs;
	}
}

