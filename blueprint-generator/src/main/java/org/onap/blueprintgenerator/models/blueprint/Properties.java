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

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import org.onap.blueprintgenerator.models.componentspec.Auxilary;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.componentspec.HealthCheck;
import org.onap.blueprintgenerator.models.componentspec.Publishes;
import org.onap.blueprintgenerator.models.componentspec.Subscribes;
import org.onap.blueprintgenerator.models.componentspec.Volumes;
import org.onap.blueprintgenerator.models.dmaapbp.DmaapStreams;
import org.onap.blueprintgenerator.models.onapbp.LogDirectory;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonInclude.Include;

import lombok.Getter; import lombok.Setter;

@Getter @Setter
@JsonInclude(value=Include.NON_NULL)
public class Properties {
	private Appconfig application_config;
	private Auxilary docker_config;
	private Object image;
	private GetInput location_id;
	private String service_component_type;
	private TreeMap<String, Object> log_info;
	private String dns_name;
	private Object replicas;
	private String name;
	private GetInput topic_name;
	private GetInput feed_name;
	ArrayList<DmaapStreams> streams_publishes;
	ArrayList<DmaapStreams> streams_subscribes;
	private TreeMap<String, Object> tls_info;
	private ResourceConfig resource_config;
	//private boolean useExisting;

	public TreeMap<String, LinkedHashMap<String, Object>> createOnapProperties(TreeMap<String, LinkedHashMap<String, Object>> inps, ComponentSpec cs, String override) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		retInputs = inps;

		//set the image
		GetInput image = new GetInput();
		image.setGet_input("image");
		this.setImage(image);
		LinkedHashMap<String, Object> img = new LinkedHashMap<String, Object>();
		img.put("type", "string");
		img.put("default", cs.getArtifacts()[0].getUri());
		retInputs.put("image", img);

		//set the location id
		GetInput location = new GetInput();
		location.setGet_input("location_id");
		this.setLocation_id(location);
		LinkedHashMap<String, Object> locMap = new LinkedHashMap();
		locMap.put("type", "string");
		locMap.put("default", "central");

		//set the log info
		GetInput logD = new GetInput();
		logD.setGet_input("log_directory");
		TreeMap<String, Object> l = new TreeMap();
		l.put("log_directory", logD);
		this.setLog_info(l);
		LinkedHashMap<String, Object> logMap = new LinkedHashMap();
		logMap.put("type", "string");
		logMap.put("default", "''");
		retInputs.put("log_directory", logMap);

		//set the replicas
		GetInput replica = new GetInput();
		replica.setGet_input("replicas");
		this.setReplicas(replica);
		LinkedHashMap<String, Object> rep = new LinkedHashMap<String, Object>();
		rep.put("type", "integer");
		rep.put("description", "number of instances");
		rep.put("default", 1);
		retInputs.put("replicas", rep);

		//set the dns name
		this.setDns_name(cs.getSelf().getName());

		//set the name
		this.setName(cs.getSelf().getName());

		//set the docker config
		Auxilary aux = cs.getAuxilary();
		if(aux.getPorts() != null) {
			retInputs = aux.createPorts(retInputs);
		}
		this.setDocker_config(aux);

		//set the app config
		Appconfig app = new Appconfig();
		retInputs = app.createAppconfig(retInputs, cs, override);
		this.setApplication_config(app);

		//set the tls info
		GetInput tls = new GetInput();
		tls.setGet_input("use_tls");
		GetInput cert = new GetInput();
		cert.setGet_input("cert_directory");
		TreeMap<String, Object> tlsInfo = new TreeMap();
		tlsInfo.put("cert_directory", cert);
		tlsInfo.put("use_tls", tls);
		this.setTls_info(tlsInfo);

		LinkedHashMap<String, Object> certMap = new LinkedHashMap();
		certMap.put("type", "string");
		certMap.put("default", "''");
		retInputs.put("cert_directory", certMap);

		LinkedHashMap<String, Object> useMap = new LinkedHashMap();
		useMap.put("type", "boolean");
		useMap.put("default", false);
		retInputs.put("use_tls", useMap);

		//set the reource config
		ResourceConfig resource = new ResourceConfig();
		retInputs = resource.createResourceConfig(retInputs, cs.getSelf().getName());
		this.setResource_config(resource);

		return retInputs;
	}

	public TreeMap<String, LinkedHashMap<String, Object>> createDmaapProperties(TreeMap<String, LinkedHashMap<String, Object>> inps, ComponentSpec cs, String override) {
		TreeMap<String, LinkedHashMap<String, Object>> retInputs = new TreeMap<String, LinkedHashMap<String, Object>>();
		retInputs = inps;

		//set the image
		GetInput image = new GetInput();
		image.setGet_input("tag_version");
		this.setImage(image);
		LinkedHashMap<String, Object> img = new LinkedHashMap<String, Object>();
		img.put("type", "string");
		img.put("default", cs.getArtifacts()[0].getUri());
		retInputs.put("tag_version", img);

		//set the log info
		GetInput logD = new GetInput();
		logD.setGet_input("log_directory");
		TreeMap<String, Object> l = new TreeMap();
		l.put("log_directory", logD);
		this.setLog_info(l);
		LinkedHashMap<String, Object> logMap = new LinkedHashMap();
		logMap.put("type", "string");
		logMap.put("default", "''");
		retInputs.put("log_directory", logMap);

		//set service component type
		String sType = cs.getSelf().getName();
		sType = sType.replace('.', '-');
		this.setService_component_type(sType);

		//set the tls info
		GetInput tls = new GetInput();
		tls.setGet_input("use_tls");
		GetInput cert = new GetInput();
		cert.setGet_input("cert_directory");
		TreeMap<String, Object> tlsInfo = new TreeMap();
		tlsInfo.put("cert_directory", cert);
		tlsInfo.put("use_tls", tls);
		this.setTls_info(tlsInfo);

		LinkedHashMap<String, Object> certMap = new LinkedHashMap();
		certMap.put("type", "string");
		certMap.put("default", "''");
		retInputs.put("cert_directory", certMap);

		LinkedHashMap<String, Object> useMap = new LinkedHashMap();
		useMap.put("type", "boolean");
		useMap.put("default", false);
		retInputs.put("use_tls", useMap);

		//set the replicas
		GetInput replica = new GetInput();
		replica.setGet_input("replicas");
		this.setReplicas(replica);
		LinkedHashMap<String, Object> rep = new LinkedHashMap<String, Object>();
		rep.put("type", "integer");
		rep.put("description", "number of instances");
		rep.put("default", 1);
		retInputs.put("replicas", rep);

//		//set the dns name
//		this.setDns_name(cs.getSelf().getName());

//		//set the name
//		this.setName(cs.getSelf().getName());

		//set the docker config
		Auxilary aux = cs.getAuxilary();
		if(aux.getPorts() != null) {
			retInputs = aux.createPorts(retInputs);
		}
		this.setDocker_config(aux);

		//set the appconfig
		Appconfig app = new Appconfig();
		retInputs = app.createAppconfig(retInputs, cs, override);
		this.setApplication_config(app);

		//set the stream publishes
		ArrayList<DmaapStreams> pubStreams = new ArrayList();
		int counter = 0;
		if(cs.getStreams().getPublishes() != null) {
			for(Publishes p: cs.getStreams().getPublishes()) {
				if(p.getType().equals("message_router") || p.getType().equals("message router")) {
					String topic = "topic" + counter;
					DmaapStreams mrStreams = new DmaapStreams();
					retInputs = mrStreams.createStreams(inps, cs, topic, p.getType(), p.getConfig_key(), p.getRoute(), 'p');
					pubStreams.add(mrStreams);
				}
				else if(p.getType().equals("data_router") || p.getType().equals("data router")){
					String feed = "feed" + counter;
					DmaapStreams drStreams = new DmaapStreams();
					retInputs = drStreams.createStreams(inps, cs, feed, p.getType(), p.getConfig_key(), p.getRoute(), 'p');
					pubStreams.add(drStreams);
				}
				counter++;
			}
		}

		//set the stream subscribes
		ArrayList<DmaapStreams> subStreams = new ArrayList();
		if(cs.getStreams().getSubscribes() != null) {
			for(Subscribes s: cs.getStreams().getSubscribes()) {
				if(s.getType().equals("message_router") || s.getType().equals("message router")) {
					String topic = "topic" + counter;
					DmaapStreams mrStreams = new DmaapStreams();
					retInputs = mrStreams.createStreams(inps, cs, topic, s.getType(), s.getConfig_key(), s.getRoute(), 's');
					subStreams.add(mrStreams);
				}
				else if(s.getType().equals("data_router") || s.getType().equals("data router")){
					String feed = "feed" + counter;
					DmaapStreams drStreams = new DmaapStreams();
					retInputs = drStreams.createStreams(inps, cs, feed, s.getType(), s.getConfig_key(), s.getRoute(), 's');
					subStreams.add(drStreams);
				}
				counter++;
			}
		}

		if(pubStreams.size() != 0) {
			this.setStreams_publishes(pubStreams);
		}
		if(subStreams.size() != 0) {
			this.setStreams_subscribes(subStreams);
		}

		//set the reource config
		ResourceConfig resource = new ResourceConfig();
		retInputs = resource.createResourceConfig(retInputs, cs.getSelf().getName());
		this.setResource_config(resource);


		return retInputs;
	}
}
