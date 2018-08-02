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
import { Component, Input, OnInit, OnChanges} from '@angular/core';
import { MdToolbarModule, MdButton, MdInputModule, MdSelectModule} from '@angular/material';
import {ValidateMetaSchemaService} from './validate-metaschema.service';
import {MetaSchemaService} from './metaschema.service';

@Component({
  selector: 'app-df-schema',
  templateUrl: './df-schema.component.html',
  styleUrls: [ './df-schema.component.css']
})
export class DFSchemaComponent implements OnInit /*, OnChanges */ {
   public dfschema = '';
   private jsonTestObject: any;
   private validJSON: boolean;
   public metaDisplay = false;
   public schemaMsg: string;
   public schemaErrMsgs: string[] = [];
   private schemaMsgColor: string;
   private schemaPassColor = '#00ff00';
   private schemaFailColor = '#ff0000';
   public metaButton = 'Display MetaSchema';
   private hideMeta = 'Hide MetaSchema';
   private displayMeta = 'Display Metaschema';
   private schemaValidate: Object;
   private validateMetaSchema: ValidateMetaSchemaService;
   private metaSchema: MetaSchemaService;


   // inline for now - TBD
   public dfmetaschema: string;
   private dfjson: string;

   constructor (validateMetaSchemaService: ValidateMetaSchemaService, metaSchemaService: MetaSchemaService) {
      this.validateMetaSchema = validateMetaSchemaService;
      this.metaSchema = metaSchemaService;
      this.dfmetaschema = this.metaSchema.currentMetaSchemaFormatted();
   }

   ngOnInit(): void {
     this.schemaMsgColor=this.schemaPassColor;
   }

   toggleMetaSchema(): void {
     this.metaDisplay = !this.metaDisplay;
     if (this.metaDisplay === true) {
       this.metaButton = this.hideMeta;
     } else {
       this.metaButton = this.displayMeta;
     }
   }

   doDFSchemaChange(ev: any) {
     this.schemaErrMsgs = [];
     this.schemaMsg = '';
     this.dfschema = ev.target.value;
     if (this.dfschema.length == 0) {
       return;
     }
     try {
       // check for JSON validity
       this.jsonTestObject = JSON.parse(this.dfschema);
       this.validJSON = true;
       this.schemaMsg = 'Valid JSON';
     } catch (jsonErrMsg) {
       this.schemaMsg = 'Invalid JSON: ' + jsonErrMsg;
       return;
     }
     if (this.jsonTestObject.hasOwnProperty('jsonschema')) {
       if (this.jsonTestObject.jsonschema.hasOwnProperty('$schema')){
         try {
           if (!(this.jsonTestObject.jsonschema.$schema === 'http://json-schema.org/draft-04/schema#'  || this.jsonTestObject.jsonschema.$schema === 'http://json-schema.org/draft-06/schema#')) {
             this.schemaMsg = 'Invalid JSON Schema Data Format -  jsonschema$schema version must be 04 or 06';
             return;
           }
         } catch(schemaVersionErr) {
            this.schemaMsg = 'Invalid JSON Schema Data Format -  jsonschema$schema version must be 04 or 06';
            return;
         }
       } else {
            this.schemaMsg = 'Invalid JSON Schema Data Format -  jsonschema$schema must be specified';
            return;
       }
     }
     if (this.validateMetaSchema.validate(this.dfschema) === false) {
       this.schemaMsg = 'Invalid Data Format Schema:';
       this.schemaErrMsgs = this.validateMetaSchema.validateMsgs();
     } else {
       this.schemaMsg = 'Valid Data Format Schema';
     }
   }
 }
