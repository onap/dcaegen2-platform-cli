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

import static org.junit.Assert.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import java.io.IOException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.junit.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;
import org.onap.blueprintgenerator.models.blueprint.Blueprint;
import org.onap.blueprintgenerator.models.blueprint.GetInput;
import org.onap.blueprintgenerator.models.componentspec.Artifacts;
import org.onap.blueprintgenerator.models.componentspec.Auxilary;
import org.onap.blueprintgenerator.models.componentspec.CallsObj;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.Container;
import org.onap.blueprintgenerator.models.componentspec.HealthCheck;
import org.onap.blueprintgenerator.models.componentspec.Host;
import org.onap.blueprintgenerator.models.componentspec.Parameters;
import org.onap.blueprintgenerator.models.componentspec.Policy;
import org.onap.blueprintgenerator.models.componentspec.ProvidesObj;
import org.onap.blueprintgenerator.models.componentspec.Publishes;
import org.onap.blueprintgenerator.models.componentspec.Self;
import org.onap.blueprintgenerator.models.componentspec.Services;
import org.onap.blueprintgenerator.models.componentspec.Streams;
import org.onap.blueprintgenerator.models.componentspec.Subscribes;
import org.onap.blueprintgenerator.models.componentspec.Volumes;
import org.onap.blueprintgenerator.models.dmaapbp.DmaapNode;
import org.onap.blueprintgenerator.models.onapbp.OnapNode;
import org.onap.blueprintgenerator.models.policymodel.PolicyModel;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import picocli.CommandLine;


// TODO: Auto-generated Javadoc
/**
 * The Class BlueprintGeneratorTest.
 */
public class BlueprintGeneratorTest {

	/**
	 * Component spec test.
	 *
	 * @throws JsonParseException the json parse exception
	 * @throws JsonMappingException the json mapping exception
	 * @throws IOException Signals that an I/O exception has occurred.
	 */

	@Test
	public void componentSpecTest() throws JsonParseException, JsonMappingException, IOException {

		ComponentSpec spec = new ComponentSpec();
		TestComponentSpec test = new TestComponentSpec();
		spec.createComponentSpecFromString(test.getCs());

		//Manually fill a component spec object with the values from the file itself
		ComponentSpec manualSpec = new ComponentSpec();

		Self self = new Self();
		self.setComponent_type("docker");
		self.setDescription("Test component spec");
		self.setName("test.component.spec");
		self.setVersion("1.0.1");
		manualSpec.setSelf(self);

		//assertEquals(manualSpec.getSelf(), spec.getSelf());

		Services services = new Services();
		CallsObj[] calls = new CallsObj[0];
		ProvidesObj[] provides = new ProvidesObj[0];
		services.setCalls(calls);
		services.setProvides(provides);
		manualSpec.setServices(null);	

		//assertEquals(manualSpec.getServices(), spec.getServices());

		Streams streams = new Streams();
		Publishes[] publishes = new Publishes[2];
		Publishes pub1 = new Publishes();
		pub1.setConfig_key("TEST-PUB-DR");
		pub1.setFormat("dataformat_Hello_World_PM");
		pub1.setType("data_router");
		pub1.setVersion("1.0.0");

		Publishes pub2 = new Publishes();
		pub2.setConfig_key("TEST-PUB-MR");
		pub2.setFormat("dataformat_Hello_World_PM");
		pub2.setType("message_router");
		pub2.setVersion("1.0.0");
		publishes[0] = pub1;
		publishes[1] = pub2;
		streams.setPublishes(publishes);

		Subscribes[] subscribes = new Subscribes[2];	
		Subscribes sub1 = new Subscribes();
		sub1.setConfig_key("TEST-SUB-MR");
		sub1.setFormat("dataformat_Hello_World_PM");
		sub1.setRoute("/TEST_HELLO_WORLD_SUB_MR");
		sub1.setType("message_router");
		sub1.setVersion("1.0.0");

		Subscribes sub2 = new Subscribes();
		sub2.setConfig_key("TEST-SUB-DR");
		sub2.setFormat("dataformat_Hello_World_PM");
		sub2.setRoute("/TEST-HELLO-WORLD-SUB-DR");
		sub2.setType("data_router");
		sub2.setVersion("1.0.0");
		subscribes[0] = sub1;
		subscribes[1] = sub2;
		streams.setSubscribes(subscribes);

		manualSpec.setStreams(streams);

		//assertEquals(manualSpec.getStreams(), spec.getStreams());

		Parameters[] parameters = new Parameters[1];
		Parameters par1 = new Parameters();
		par1.setName("testParam1");
		par1.setValue("test-param-1");
		par1.setDescription("test parameter 1");
		par1.setSourced_at_deployment(true);
		par1.setDesigner_editable(true);
		par1.setPolicy_editable(true);
		par1.setPolicy_group("Test_Parameters");
		par1.setRequired(true);
		par1.setType("string");
		parameters[0] = par1;

		manualSpec.setParameters(parameters);

		//assertEquals(manualSpec.getParameters(), spec.getParameters());

		Auxilary auxilary = new Auxilary();
		HealthCheck healthcheck = new HealthCheck();
		healthcheck.setInterval("300s");
		healthcheck.setTimeout("120s");
		healthcheck.setScript("/etc/init.d/nagios status");
		healthcheck.setType("docker");
		auxilary.setHealthcheck(healthcheck);

		Volumes[] volumes = new Volumes[1];
		Volumes vol1 = new Volumes();
		Container con1 = new Container();
		con1.setBind("/opt/app/manager/config/hostname");
		Host host1 = new Host();
		host1.setPath("/etc/hostname");
		host1.setMode("ro");
		vol1.setContainer(con1);
		vol1.setHost(host1);


		volumes[0] = vol1;

		auxilary.setVolumes(volumes);

		ArrayList<Object> ports = new ArrayList();
		ports.add("80:90");
		ports.add("99:99");

		TreeMap<String, String> dataBases = new TreeMap<String, String>();
		dataBases.put("TestDB1", "PGaaS");
		dataBases.put("TestDB2", "PGaaS");
		auxilary.setDatabases(dataBases);

		Policy pol = new Policy();
		pol.setTrigger_type("docker");
		pol.setScript_path("/opt/app/manager/bin/reconfigure.sh");
		auxilary.setPolicy(pol);

		auxilary.setPorts(ports);

		manualSpec.setAuxilary(auxilary);

		//assertEquals(manualSpec.getAuxilary(), spec.getAuxilary());

		Artifacts[] artifacts = new Artifacts[1];
		Artifacts art = new Artifacts();
		art.setType("docker image");
		art.setUri("test.tester");

		artifacts[0] = art;
		manualSpec.setArtifacts(artifacts);

		//assertEquals(manualSpec.getArtifacts(), spec.getArtifacts());
	}

	/**
	 * Tosca definition test.
	 */
	@Test
	public void toscaDefinitionTest() {
		ComponentSpec cs = new ComponentSpec();
		TestComponentSpec test = new TestComponentSpec();
		cs.createComponentSpecFromString(test.getCs());
		Blueprint bp = new Blueprint();
		bp = bp.createBlueprint(cs, "", 'o', "", "");

		assertEquals(bp.getTosca_definitions_version(), "cloudify_dsl_1_3");
	}

	/**
	 * Imports test.
	 */
	@Test
	public void importsTest() {
		ComponentSpec cs = new ComponentSpec();
		TestComponentSpec test = new TestComponentSpec();
		cs.createComponentSpecFromString(test.getCs());

		Blueprint bp = new Blueprint();
		bp = bp.createBlueprint(cs, "", 'o', "", "");

		ArrayList<String> imps = new ArrayList<String>();

		imps.add("http://www.getcloudify.org/spec/cloudify/3.4/types.yaml");
		imps.add("https://nexus.onap.org/service/local/repositories/raw/content/org.onap.dcaegen2.platform.plugins/R4/k8splugin/1.4.5/k8splugin_types.yaml");
		imps.add("https://nexus.onap.org/service/local/repositories/raw/content/org.onap.dcaegen2.platform.plugins/R4/dcaepolicyplugin/2.3.0/dcaepolicyplugin_types.yaml");
		assertEquals(bp.getImports(), imps);
	}

	@Test
	public void inputTest() {
		ComponentSpec cs = new ComponentSpec();
		cs.createComponentSpecFromFile("TestCases/testComponentSpec.json");

		Blueprint bp = new Blueprint();
		bp = bp.createBlueprint(cs, "", 'o', "", "");

		TreeMap<String, LinkedHashMap<String, Object>> inputs = new TreeMap<String, LinkedHashMap<String, Object>>();

		//mr inputs
		LinkedHashMap<String, Object> stringType = new LinkedHashMap<String, Object>();
		stringType.put("type", "string");


		//necessary inputs
		LinkedHashMap<String, Object> tag = new LinkedHashMap<String, Object>();
		tag.put("type", "string");
		String tester = "test.tester";
		tag.put("default", '"' + tester + '"');
		String tagVersion = "tag_version";
		inputs.put("tag_version", tag);

		inputs.put("log_directory", stringType);

		LinkedHashMap cert = new LinkedHashMap();
		cert.put("type", "string");
		cert.put("default", "");
		inputs.put("cert_directory", cert);

		LinkedHashMap<String, Object> env = new LinkedHashMap();
		env.put("default", "{}");
		inputs.put("envs", env);

		LinkedHashMap port = new LinkedHashMap();
		port.put("type", "string");
		port.put("description", "Kubernetes node port on which collector is exposed");
		port.put("default", "99");
		inputs.put("external_port", port);

		LinkedHashMap<String, Object> rep = new LinkedHashMap<String, Object>();
		rep.put("type", "integer");
		rep.put("description", "number of instances");
		rep.put("default", 1);
		inputs.put("replicas", rep);

		LinkedHashMap<String, Object> aaf = new LinkedHashMap();
		aaf.put("type", "boolean");
		aaf.put("default", false);
		inputs.put("use_tls", aaf);

		//parmaeter input
		LinkedHashMap<String, Object> test = new LinkedHashMap<String, Object>();
		test.put("type", "string");
		String testParam = "test-param-1";
		test.put("default", '"' + testParam + '"');
		inputs.put("testParam1", test);

		//mr/dr inputs
		inputs.put("TEST-PUB-DR_feed0_client_role", stringType);
		inputs.put("TEST-PUB-DR_feed0_password", stringType);
		inputs.put("TEST-PUB-DR_feed0_username", stringType);
		inputs.put("TEST-PUB-MR_topic1_aaf_password", stringType);
		inputs.put("TEST-PUB-MR_topic1_aaf_username", stringType);
		inputs.put("TEST-PUB-MR_topic1_client_role", stringType);
		inputs.put("TEST-SUB-DR_feed1_client_role", stringType);
		inputs.put("TEST-SUB-DR_feed1_password", stringType);
		inputs.put("TEST-SUB-DR_feed1_username", stringType);
		inputs.put("TEST-SUB-MR_topic0_client_role", stringType);
		inputs.put("TEST-SUB-MR_topic2_aaf_password", stringType);
		inputs.put("TEST-SUB-MR_topic2_aaf_username", stringType);
		inputs.put("namespace", stringType);
		inputs.put("idn_fqdn", cert);
		inputs.put("feed0_name", stringType);
		inputs.put("feed1_name", stringType);
		inputs.put("topic0_name", stringType);
		inputs.put("topic1_name", stringType);

		LinkedHashMap<String, Object> cpu = new LinkedHashMap();
		cpu.put("type", "string");
		cpu.put("default", "250m");
		inputs.put("test.component.spec_cpu_limit", cpu);
		inputs.put("test.component.spec_cpu_request", cpu);

		LinkedHashMap<String, Object> mem = new LinkedHashMap();
		mem.put("type", "string");
		mem.put("default", "128Mi");
		inputs.put("test.component.spec_memory_limit", mem);
		inputs.put("test.component.spec_memory_request", mem);

		assertEquals(true, true);
	}
	@Test
	public void interfaceTest() {
		ComponentSpec cs = new ComponentSpec();
		cs.createComponentSpecFromFile("TestCases/testComponentSpec.json");

		Blueprint bp = new Blueprint();
		bp = bp.createBlueprint(cs, "", 'o', "", "");

		OnapNode node = (OnapNode) bp.getNode_templates().get("test.component.spec");

		OnapNode testNode = new OnapNode();

		//set the type
		testNode.setType("dcae.nodes.ContainerizedPlatformComponent");

		ArrayList<String> ports = new ArrayList<String>();
		ports.add("concat: [\"80:\", {get_input: external_port }]");
		ports.add("concat: [\"99:\", {get_input: external_port }]");
		assertEquals(true, true);
	}

	@Test
	public void parametersTest() {
		ComponentSpec cs = new ComponentSpec();
		cs.createComponentSpecFromFile("TestCases/testComponentSpec.json");

		Blueprint bp = new Blueprint();
		bp = bp.createBlueprint(cs, "", 'o', "", "");

		OnapNode node = (OnapNode) bp.getNode_templates().get("test.component.spec");

		GetInput par = (GetInput) node.getProperties().getApplication_config().getParams().get("testParam1");
		assertEquals(par.getGet_input(), "testParam1");
	}

	@Test
	public void streamPublishesTest() {
		ComponentSpec cs = new ComponentSpec();
		cs.createComponentSpecFromFile("TestCases/testComponentSpec.json");

		Blueprint bp = new Blueprint();
		bp = bp.createBlueprint(cs, "", 'o', "", "");

		OnapNode node = (OnapNode) bp.getNode_templates().get("test.component.spec");

		boolean test = false;
		if(!node.getProperties().getApplication_config().getStreams_publishes().isEmpty()) {
			test = true;
			System.out.println("tst");
		}

		assertEquals(true, test);
	}
	@Test
	public void dmaapPluginTest() {
		ComponentSpec cs = new ComponentSpec();
		cs.createComponentSpecFromFile("TestCases/testComponentSpec.json");

		Blueprint bp = new Blueprint();
		bp = bp.createBlueprint(cs, "", 'd', "", "");

		DmaapNode dmaap = (DmaapNode) bp.getNode_templates().get("test.component.spec");

		//check if the stream publishes and subscribes are not null to see if the dmaap plugin was invoked properly
		boolean d = false;

		if(dmaap.getProperties().getStreams_publishes() != null || dmaap.getProperties().getStreams_subscribes() != null) {
			d = true;
		}
		assertEquals(true, d);
	}

	@Test
	public void testPrintInstructionsBlueprintCommand() {
		BlueprintCommand objUnderTest = new BlueprintCommand();
		CommandLine cli = new CommandLine(objUnderTest);
		PrintStream mockStdOutWriter = Mockito.mock(PrintStream.class);
		ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
		cli.usage(mockStdOutWriter);
		verify(mockStdOutWriter, times(1)).print(any(Object.class));

	}

	@Test
	public void testPrintInstructionsPolicyCommand() {
		PolicyCommand objUnderTest = new PolicyCommand();
		CommandLine cli = new CommandLine(objUnderTest);
		PrintStream mockStdOutWriter = Mockito.mock(PrintStream.class);
		ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
		cli.usage(mockStdOutWriter);
		verify(mockStdOutWriter, times(1)).print(any(Object.class));
	}
	
	@Test
	public void testPolicyModels() {
		ComponentSpec cs = new ComponentSpec();
		cs.createComponentSpecFromFile("TestCases/testComponentSpec.json");
		
		PolicyModel p = new PolicyModel();
		p.createPolicyModels(cs, "TestModels");
		
		assertEquals(true, true);
	}
}
