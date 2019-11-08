# Blueprint Generator 

This tool allows the user to create a blueprint from a component spec json file 

# Instructions for building the tool locally
- Change directory into the root directory of the project (where the pom is located)
- Run the command: `mvn clean install`
- This will create a jar file and a tar file
- To execute the application

```bash
java -jar target/blueprint-generator-1.2.1-SNAPSHOT-executable.jar
```


# Instructions for running BlueprintGenerator:

## Instructions for running:


-Run the program on the command line with the following tags:
OPTIONS:
- -p: The path to where the final blueprint yaml file will be created (Required)
- -i: The path to the JSON spec file (required)
- -n: Name of the blueprint (optional)
- -t: the path to the import yaml file (optional)
- -d: Onvoke the dmaap plugin (optional)
- -o: The service component name override (optional)


it will look like this:

```bash
java -jar target/blueprint-generator-1.2.1-SNAPSHOT-executable.jar blueprint -p Blueprints -i ComponentSpecs/TestComponentSpec.json -n HelloWorld -d
```

This command will create a blueprint from the component spec TestComponentSpec. The blueprint file name will be called HelloWorld.yaml and it will be in the directory Blueprints. The blueprint will also contain the DMaaP plugin.

## Extra information:
- The component spec must be of the same format as stated in the onap [readthedocs](https://onap.readthedocs.io/en/latest/submodules/dcaegen2.git/docs/sections/components/component-specification/common-specification.html#working-with-component-specs) page 
- If the tag says required then the program will not run without those tags being there
- If the tag says optional then it is not necessary to run the program with those tags
- If you do not add a -n tag the blueprint name will default to what it is in the component spec
- If the directory you specified in the -p tag does not already exist the directory will be created for you
- The -t flag will override the default imports set for the blueprints. To see an example of how the import yaml file should be structured see the testImports.yaml file under the folder TestCases.


#Instructions for policy models

-Run the program on the command line with the following tags:
OPTIONS:
- -i: The path to the JSON spec file (required)
- -p: The output path for all of the models (required)

it will look like this:

```bash
java -jar target/blueprint-generator-1.2.1-SNAPSHOT-executable.jar policy -p models -i ComponentSpecs/TestComponentSpec.json
```

This command will create a directory called models and put the policy models created from the component spec given in that directory. (A component spec may generate multiple policy models)