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
import {DFJSONInputComponent} from './df-jsoninput.component';



import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

describe('DFSJSONInputComponent Tests', function () {
  let de: DebugElement;
  let comp: DFJSONInputComponent;
  let fixture: ComponentFixture<DFJSONInputComponent>;

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
                      DFJSONInputComponent,

                   ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DFJSONInputComponent);
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
      expect(comp.schemaMsg).toMatch("Invalid Data Format Schema") ;
     });
     it('schema must have JSON schema ', () => {
       let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},  "json1schema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false  }}'}};
       comp.doDFSchemaChange(ev);
       expect(comp.schemaMsg).toMatch("Invalid Schema - must specify jsonschema") ;
      });
      it('JSON schema must be 04', () => {
        let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "jsonschema": {  "$schema": "http://json-schema.org/draft-05/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false }}'}};
        comp.doDFSchemaChange(ev);
        expect(comp.schemaMsg).toMatch(/Invalid JSON Schema Data Format -  jsonschema\$schema version must be 04/) ;
       });
     it('should fail if JSON input and no schema', () => {
       let ev = {target: {name: "test", value: '{}'}};
       comp.doDFJSONChange(ev);
       expect(comp.jsonMsg).toMatch("Enter a Valid Schema") ;
      });
      it('should validate if JSON input and match valid schema', () => {
        let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false }}'}};
        comp.doDFSchemaChange(ev);
        let jev = {target: {name: "test", value: '{"raw-text": "test"}'}};
        comp.doDFJSONChange(jev);
        expect(comp.jsonMsg).toMatch("JSON Input Validated") ;
       });
       it('should not validate if JSON input does not match valid schema', () => {
         let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false }}'}};
         comp.doDFSchemaChange(ev);
         let jev = {target: {name: "test", value: '{"badraw-text": "test"}'}};
         comp.doDFJSONChange(jev);
         expect(comp.jsonMsg).toMatch("JSON Input does not match Schema") ;
        });
        it('should recover if schema becomes valid', () => {
          let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false  }}'}};
          comp.doDFSchemaChange(ev);
          expect(comp.schemaMsg).toMatch("Invalid Data Format Schema") ;
          let jev = {target: {name: "test", value: '{"raw-text": "test"}'}};
          comp.doDFJSONChange(jev);
          let ev2 = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false }}'}};
          comp.doDFSchemaChange(ev2);
          expect(comp.jsonMsg).toMatch("JSON Input Validated") ;
          expect(comp.schemaMsg).toMatch("Valid Data Format Schema") ;
         });
         it('should fail if schema becomes invalid', () => {
           let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false }}'}};
           comp.doDFSchemaChange(ev);
           let jev = {target: {name: "test", value: '{"raw-text": "test"}'}};
           comp.doDFJSONChange(jev);
           ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "json1schema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false }}'}};
           comp.doDFSchemaChange(ev);
           expect(comp.jsonMsg).toMatch("Enter a valid Schema") ;
          });
          it('should  validate if JSON input is fixed to match valid schema', () => {
            let ev = {target: {name: "test", value: '{"self": {  "name": "CUDA Simple JSON Example","version": "1.0.0","description": "An example of unnested JSON schema for CUDA Input and output"},"dataformatversion": "1.0.0",  "jsonschema": {  "$schema": "http://json-schema.org/draft-04/schema#","type": "object",  "properties": {"raw-text": {"type": "string"  }  },  "required": ["raw-text"],  "additionalProperties": false }}'}};
            comp.doDFSchemaChange(ev);
            let jev = {target: {name: "test", value: '{"badraw-text": "test"}'}};
            comp.doDFJSONChange(jev);
            expect(comp.jsonMsg).toMatch("JSON Input does not match Schema") ;
            jev = {target: {name: "test", value: '{"raw-text": "test"}'}};
            comp.doDFJSONChange(jev);
            expect(comp.jsonMsg).toMatch("JSON Input Validated") ;
           });
});
