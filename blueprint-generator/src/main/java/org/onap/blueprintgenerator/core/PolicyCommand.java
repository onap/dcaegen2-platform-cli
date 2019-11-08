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

import org.onap.blueprintgenerator.models.componentspec.ComponentSpec;
import org.onap.blueprintgenerator.models.policymodel.PolicyModel;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

@Command(name = "policy", description = "Command used to generate policy model from component spec")
public class PolicyCommand implements Runnable{
    @Option(names = {"-i", "--component-spec"}, description = "Path to component spec file", required = true)
    private String componentSpecPath;

    @Option(names = {"-p", "--model-path"}, description = "Path to directory that models are output to", required = true)
    private String modelOutputPath;

    @Override
    public void run() {
        ComponentSpec inboundComponentSpec = new ComponentSpec();
        inboundComponentSpec.createComponentSpecFromFile(componentSpecPath);
        new PolicyModel().createPolicyModels(inboundComponentSpec, this.modelOutputPath);
    }
}
