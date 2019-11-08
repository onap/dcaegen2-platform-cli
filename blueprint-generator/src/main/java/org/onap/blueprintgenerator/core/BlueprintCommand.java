/*-
 * ============LICENSE_START=======================================================
 *  Copyright (C) 2019 Nordix Foundation.
 * ================================================================================
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * SPDX-License-Identifier: Apache-2.0
 * ============LICENSE_END=========================================================
 */

package org.onap.blueprintgenerator.core;

import org.onap.blueprintgenerator.models.blueprint.Blueprint;
import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(name = "blueprint", description = "Command used to generate blueprints from component spec")
public class BlueprintCommand implements Runnable {
    private static final char STANDARD_BLUEPRINT = 'o';
    private static final char DMAAP_BLUEPRINT = 'd';

    @Option(names = {"-i", "--component-spec"}, description = "Path to component spec file", required = true)
    private String componentSpecPath;

    @Option(names = {"-p", "--blueprint-path"}, description = "Path to directory that blueprints are output to", required = true)
    private String blueprintOutputPath;

    @Option(names = {"-n", "--blueprint-name"}, description = "Name of the blueprint", defaultValue = "")
    private String blueprintName;

    @Option(names = {"-t", "--imports"}, description = "Path to the import file", defaultValue = "")
    private String importsPath;

    @Option(names={"-o", "--service-name-override"}, description="Value used to override the service name", defaultValue = "")
    private String serviceNameOverride;

    @Option(names={"-d", "--dmaap-plugin"}, description = "Flag used to indicate blueprint uses the DMaaP plugin.")
    private boolean dmaapPlugin;

    @Override
    public void run() {
        ComponentSpec inboundComponentSpec = new ComponentSpec();
        inboundComponentSpec.createComponentSpecFromFile(componentSpecPath);
        System.out.println(dmaapPlugin ? DMAAP_BLUEPRINT : STANDARD_BLUEPRINT);
        Blueprint generatedBlueprint = new Blueprint().createBlueprint(inboundComponentSpec, this.blueprintName,
                dmaapPlugin ? DMAAP_BLUEPRINT : STANDARD_BLUEPRINT, importsPath, serviceNameOverride);
        generatedBlueprint.blueprintToYaml(blueprintOutputPath, this.blueprintName, inboundComponentSpec);
    }
}
