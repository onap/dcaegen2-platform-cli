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

import java.util.ArrayList;


import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter; import lombok.Setter;
import lombok.NoArgsConstructor;

// TODO: Auto-generated Javadoc
/**
 * The Class Parameters.
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
 * Instantiates a new parameters.
 */
@NoArgsConstructor

/**
 * Instantiates a new parameters.
 *
 * @param name the name
 * @param value the value
 * @param description the description
 * @param sourced_at_deployment the sourced at deployment
 * @param designer_editable the designer editable
 * @param policy_editable the policy editable
 * @param required the required
 * @param type the type
 * @param policy_group the policy group
 * @param policy_schema the policy schema
 * @param entry_schema the entry schema
 * @param constraints the constraints
 */
@JsonInclude(value=Include.NON_NULL)
//Called in component Spec Object
public class Parameters {
	
	/** The name. */
	private String name;
	
	/** The value. */
	private Object value;
	
	/** The description. */
	private String description;
	
	/** The sourced at deployment. */
	private boolean sourced_at_deployment;
	
	/** The designer editable. */
	private boolean designer_editable;
	
	/** The policy editable. */
	private boolean policy_editable;
	
	/** The required. */
	private boolean required;
	
	/** The type. */
	private String type;
	
	/** The policy group. */
	private String policy_group;
	
	/** The policy schema. */
	private PolicySchemaObj[] policy_schema;
	
	/** The entry schema. */
	private EntrySchemaObj[] entry_schema;
	
	/** The constraints. */
	private ConstraintsObj[] constraints;
}
