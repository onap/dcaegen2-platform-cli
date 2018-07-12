# DCAE Data Format Validator

# Purpose & Responsibilities 
The purposes of this repo is provide tools for creating and checking DCAE Data Format Schema used by the DCAP CDAP Broker to define user data formats 
The build is currently done on Windows but since node.js and docker are widely supported a similar process should allow builds in other environments 

# DCAE Data Format Schema Tool 
The DCAE Data Format Schema Tool is a web application that checks the validity of a user created Data Format Schema.   Schemas can define JSON, delimited, XML, and unstructured data. 
DCAE Data Format Schemas that define JSON schema can be  checked against JSON input

## Installation and build on Windows 
It is assumed that node.js and docker Toolkit are installed
After the git repo is cloned, cd to the dcaedftool directory and issue:
``` 
    npm install 
``` 
to load the necessary libraries. Note that the latest libraries will be loaded.  If there is a problem the libraries used for testing can be loaded.  They are recorded in package-lock.json.  There was a problem once when a Material 2 library was upgraded.
## Regression testing on Windows
To test use the following command to run the Jasmine/karma regression suite.  This currently tests the program logic.   Protractor tests may follow...
``` 
   ng test 
``` 
## GUI testing using node.js 
To test under node.js using localhost:4200, issue: 
``` 
   ng serve
``` 
##  Docker build - remember to update the image version
To build a Docker image using nginx as a static page server issue:
``` 
   . ./dockerbuild.sh
``` 
## Docker windows testing - remember to update the image version
``` 
   sh dockerrun.sh
``` 
## To get the local IP address for testing - use 8080 for the port 
``` 
   docker-machine ip box 
``` 
## Use docker push to export to production 
