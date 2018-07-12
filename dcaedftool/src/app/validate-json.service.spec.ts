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
import {ValidateJSONService} from './validate-json.service';


describe('ValidateJSONService test suite', function () {
  let service: ValidateJSONService;

  beforeEach(() => {
    service = new ValidateJSONService;
  });

  it('should create service', () => expect(service).toBeDefined() );

  it('should validate valid json', () => {
    var jsonString = '{"testjson": "teststring"}'
    expect(service.validate(jsonString)).toBe(true) ;
    expect(service.validateMsgs()).toMatch('Valid JSON') ;
  });
  it('should fail to validate invalid json', () => {
    var jsonString = '"testjson": "teststring"}'
    expect(service.validate(jsonString)).toBe(false) ;
    expect(service.validateMsgs()).toMatch('Invalid JSON/*') ;
  });
});
