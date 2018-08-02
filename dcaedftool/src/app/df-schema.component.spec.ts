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
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import {HttpModule} from '@angular/http';  // for future
import {FormsModule, ReactiveFormsModule} from '@angular/forms'; // for future
import {BrowserAnimationsModule} from '@angular/platform-browser/animations'; // for future
import { MaterialModule } from '@angular/material';
import { FlexLayoutModule } from '@angular/flex-layout';
import { RouterModule, Routes } from '@angular/router';
import { APP_BASE_HREF } from '@angular/common';

import {ValidateMetaSchemaService} from './validate-metaschema.service';
import {ValidateJSONService} from './validate-json.service';
import {MetaSchemaService} from './metaschema.service';
import {DFSchemaComponent} from './df-schema.component';



import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

describe('DFSchemaComponent Tests', function () {
  let de: DebugElement;
  let comp: DFSchemaComponent;
  let fixture: ComponentFixture<DFSchemaComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports:      [  BrowserModule,
        BrowserAnimationsModule,
        FormsModule,
        HttpModule,
        ReactiveFormsModule,
        FlexLayoutModule,
        MaterialModule,

        ],
      providers: [{provide: APP_BASE_HREF, useValue: '/'},
      ValidateMetaSchemaService,
      ValidateJSONService,
      MetaSchemaService
                  ],
      declarations: [
                      DFSchemaComponent,

                   ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DFSchemaComponent);
    comp = fixture.componentInstance;
    //de = fixture.debugElement.query(By.css('h1'));
  });

  it('should create component', () => expect(comp).toBeDefined() );

 it('should have no metaschema display as default', () => {
      expect(comp.metaButton).toMatch('Display MetaSchema');
  });
  it('should  metaschema display after toggle', () => {
       comp.toggleMetaSchema();
       expect(comp.metaButton).toMatch('Hide MetaSchema');
   });
   it('should validate valid schema', () => {
     let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false }}'}};
     comp.doDFSchemaChange(ev);
     expect(comp.schemaMsg).toMatch("Valid Data Format Schema") ;
    });
    it('should not validate an invalid schema', () => {
      let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false  }}'}};
      comp.doDFSchemaChange(ev);
      expect(comp.schemaMsg).toMatch("Invalid Data Format Schema:") ;
     });
     it('jsonschema must be 04 or 06 schema', () => {
       let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},  "jsonschema": {  "$schema": "http://json-schema.org/draft-05/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false  }}'}};
       comp.doDFSchemaChange(ev);
       expect(comp.schemaMsg).toMatch(/Invalid JSON Schema Data Format -  jsonschema\$schema version must be 04 or 06/) ;
    });
});
