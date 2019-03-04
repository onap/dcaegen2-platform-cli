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




import lombok.Getter;
import lombok.Setter;

@Getter @Setter
public class TestComponentSpec {
	private String cs = "{\r\n" + 
			"	\"self\": {\r\n" + 
			"		\"component_type\": \"docker\",\r\n" + 
			"		\"description\": \"Test component spec\",\r\n" + 
			"		\"name\": \"test.component.spec\",\r\n" + 
			"		\"version\": \"1.0.1\"\r\n" + 
			"	},\r\n" + 
			"\r\n" + 
			"	\"service\": {\r\n" + 
			"		\"calls\": [],\r\n" + 
			"		\"provides\": []\r\n" + 
			"	},\r\n" + 
			"\r\n" + 
			"	\"streams\": {\r\n" + 
			"				\"publishes\": [{\r\n" + 
			"				\"config_key\": \"TEST-PUB-DR\",\r\n" + 
			"				\"format\": \"dataformat_Hello_World_PM\",\r\n" + 
			"				\"type\": \"data_router\",\r\n" + 
			"				\"version\": \"1.0.0\"\r\n" + 
			"			},\r\n" + 
			"			{\r\n" + 
			"				\"config_key\": \"TEST-PUB-MR\",\r\n" + 
			"				\"format\": \"dataformat_Hello_World_PM\",\r\n" + 
			"				\"type\": \"message_router\",\r\n" + 
			"				\"version\": \"1.0.0\"\r\n" + 
			"			}\r\n" + 
			"		],\r\n" + 
			"\r\n" + 
			"		\"subscribes\": [{\r\n" + 
			"				\"config_key\": \"TEST-SUB-MR\",\r\n" + 
			"				\"format\": \"dataformat_Hello_World_PM\",\r\n" + 
			"				\"route\": \"/TEST_HELLO_WORLD_SUB_MR\",\r\n" + 
			"				\"type\": \"message_router\",\r\n" + 
			"				\"version\": \"1.0.0\"\r\n" + 
			"			},\r\n" + 
			"			{\r\n" + 
			"				\"config_key\": \"TEST-SUB-DR\",\r\n" + 
			"				\"format\": \"dataformat_Hello_World_PM\",\r\n" + 
			"				\"route\": \"/TEST-HELLO-WORLD-SUB-DR\",\r\n" + 
			"				\"type\": \"data_router\",\r\n" + 
			"				\"version\": \"1.0.0\"\r\n" + 
			"			}		\r\n" + 
			"		]\r\n" + 
			"	},\r\n" + 
			"\r\n" + 
			"	\"parameters\":\r\n" + 
			"	[\r\n" + 
			"		{\r\n" + 
			"			\"name\": \"testParam1\",\r\n" + 
			"			\"description\": \"test parameter 1\",\r\n" + 
			"			\"value\": \"test-param-1\",\r\n" + 
			"			\"type\": \"string\",\r\n" + 
			"			\"sourced_at_deployment\": true,\r\n" + 
			"			\"designer_editable\": true,\r\n" + 
			"			\"policy_editable\": true,\r\n" + 
			"			\"policy_group\": \"Test_Parameters\",\r\n" + 
			"			\"required\": true\r\n" + 
			"		}\r\n" + 
			"	],\r\n" + 
			"\r\n" + 
			"	\"auxilary\": {\r\n" + 
			"		\"healthcheck\": {\r\n" + 
			"			\"type\": \"docker\",\r\n" + 
			"			\"interval\": \"300s\",\r\n" + 
			"			\"timeout\": \"120s\",\r\n" + 
			"			\"script\": \"/etc/init.d/nagios status\"\r\n" + 
			"		},\r\n" + 
			"\r\n" + 
			"		\"databases\" : {\r\n" + 
			"          \"TestDB1\": \"PGaaS\",\r\n" + 
			"          \"TestDB2\": \"PGaaS\"\r\n" + 
			"        },\r\n" + 
			"\r\n" + 
			"		\"policy\": {\r\n" + 
			"			\"trigger_type\": \"docker\",\r\n" + 
			"			\"script_path\": \"/opt/app/manager/bin/reconfigure.sh\"\r\n" + 
			"		},\r\n" + 
			"		\"volumes\": [\r\n" + 
			"			{\r\n" + 
			"				\"container\": {\r\n" + 
			"					\"bind\": \"/opt/app/manager/config/hostname\"\r\n" + 
			"				},\r\n" + 
			"				\"host\": {\r\n" + 
			"					\"path\": \"/etc/hostname\",\r\n" + 
			"					\"mode\": \"ro\"\r\n" + 
			"				}\r\n" + 
			"			}\r\n" + 
			"\r\n" + 
			"		],\r\n" + 
			"		\"ports\": [\r\n" + 
			"			\"80:80\"\r\n" + 
			"		]\r\n" + 
			"	},\r\n" + 
			"\r\n" + 
			"	    \"artifacts\": [{\r\n" + 
			"		\"type\": \"docker image\",\r\n" + 
			"		\"uri\": \"test.tester\"\r\n" + 
			"	}]	\r\n" + 
			"\r\n" + 
			"}";
}
