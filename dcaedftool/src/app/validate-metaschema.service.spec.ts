// org.onap.dcae
// ============LICENSE_START====================================================
// Copyright (c) 2018 AT&T Intellectual Property. All rights reserved.
// =============================================================================
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// ============LICENSE_END======================================================
//
// ECOMP is a trademark and service mark of AT&T Intellectual Property.
import { Injectable } from '@angular/core';
import {ValidateMetaSchemaService} from './validate-metaschema.service';
import {MetaSchemaService} from './metaschema.service';
import {ValidateJSONService} from './validate-json.service';

describe('ValidateMetaSchemaService test suite', function () {
  let service: ValidateMetaSchemaService;

  beforeEach(() => {
    let jsonservice = new ValidateJSONService;
    let metaservice = new MetaSchemaService;
    service = new ValidateMetaSchemaService(metaservice, jsonservice);
  });

  it('should create service', () => expect(service).toBeDefined() );


  it('should fail to validate invalid json', () => {
    var jsonString = '"testjson": "teststring"}'
    expect(service.validate(jsonString)).toBe(false) ;
    expect(service.validateMsgs()).toMatch("Invalid JSON.*");
  });
  it('should validate valid JSON schema', () => {
    var jsonString = '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false  }}'
    expect(service.validate(jsonString)).toBe(true) ;
  });

  it('should validate valid reference schema', () => {
    var jsonString ='{  "self": {  "name": "Common Event Format Definition",  "version": "25.0.0",  "description": "Common Event Format Definition"},  "dataformatversion": "1.0.0",  "reference": {      "name": "Common Event Format",    "format": "JSON",    "version": "25.0.0"     }}';
    expect(service.validate(jsonString)).toBe(true) ;
  });

  it('should validate valid delimited schema', () => {
    var jsonString ='{"self": {"name": "Delimited Format Example", "version": "1.0.0",  "description": "Delimited format example just for testing"  },  "dataformatversion": "1.0.0",  "delimitedschema": {  "delimiter": "|",  "fields": [{    "name": "field1",  "description": "test field1",  "fieldtype": "string"  }, {  "name": "field2",  "description": "test field2",  "fieldtype": "boolean"  }]  }  }'
    expect(service.validate(jsonString)).toBe(true) ;
  });

  it('should validate valid unstructured schema', () => {
    var jsonString ='{ "self": {  "name": "CUDA Unstructured Text Example","version": "25.0.0",  "description": "An example of a unstructured text used for both input and output for CUDA"},  "dataformatversion": "1.0.0","unstructured": {  "encoding": "UTF-8"}}';
    expect(service.validate(jsonString)).toBe(true) ;
  });

  it('should fail to validate invalid schema', () => {
    var jsonString = '{"testjson": "teststring"}'
    expect(service.validate(jsonString)).toBe(false) ;
  });

});
