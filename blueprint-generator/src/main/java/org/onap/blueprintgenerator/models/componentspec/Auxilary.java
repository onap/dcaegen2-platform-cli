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


import java.util.TreeMap;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter; import lombok.Setter;
import lombok.NoArgsConstructor;

// TODO: Auto-generated Javadoc
/* (non-Javadoc)
 * @see java.lang.Object#toString()
 */
@Getter @Setter

/* (non-Javadoc)
 * @see java.lang.Object#toString()
 */


/**
 * Instantiates a new auxilary.
 */
@NoArgsConstructor

/**
 * Instantiates a new auxilary.
 *
 * @param healthcheck the healthcheck
 * @param volumes the volumes
 * @param policy the policy
 * @param ports the ports
 * @param reconfigs the reconfigs
 * @param databases the databases
 */

@JsonInclude(value=Include.NON_NULL)
//Called in component Spec Object
public class Auxilary {
	
	/** The healthcheck. */
	private HealthCheck healthcheck;
	
	/** The volumes. */
	private Volumes[] volumes;
	
	/** The policy. */
	private Policy policy;
	
	/** The ports. */
	private String[] ports;
	
	/** The reconfigs. */
	private ReconfigsObj reconfigs;
	
	/** The databases. */
	@JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
	private TreeMap<String, String> databases;
	


}
