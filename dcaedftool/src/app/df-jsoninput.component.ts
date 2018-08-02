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
import {ValidateJSONService} from './validate-json.service';
import {MetaSchemaService} from './metaschema.service';
import * as Ajv from 'ajv';

@Component({
  selector: 'app-df-jsoninput',
  templateUrl: './df-jsoninput.component.html',
  styleUrls: [ './df-jsoninput.component.css']
})
export class DFJSONInputComponent implements OnInit /*, OnChanges */ {

  public dfschema = '';
  private jsonTestObject: any;
  private validJSON = false;
  public metaDisplay = false;
  public metaButton = 'Display MetaSchema';
  public schemaMsg: string;
  public schemaErrMsgs: string[] = [];
  private ajvService: any;
  private hideMeta = 'Hide MetaSchema';
  private displayMeta = 'Display Metaschema';
  private schemaValidate: Object;
  private validateMetaSchema: ValidateMetaSchemaService;
  private jsonValidate: ValidateJSONService;
  private metaSchema: MetaSchemaService;
  private validSchema = false;
  public dfmetaschema: string;
  public dfjson: string;
  public jsonMsg: string;
  public jsonErrMsgs: string[] = [];

  constructor (validateMetaSchemaService: ValidateMetaSchemaService, validateJSONService: ValidateJSONService, metaSchemaService: MetaSchemaService) {
      this.validateMetaSchema = validateMetaSchemaService;
      this.metaSchema = metaSchemaService;
      this.dfmetaschema = this.metaSchema.currentMetaSchemaFormatted();
      this.jsonValidate = validateJSONService;
  }


  ngOnInit(): void {
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
    this.schemaMsg = '';
    this.schemaErrMsgs = [];
    this.validSchema = false;
    this.dfschema = ev.target.value;
    if (this.dfschema.length == 0) {
      if (this.validJSON) {
        this.jsonMsg = 'Enter a Valid Schema';
        this.jsonErrMsgs = [];
      }
      return;
    }
    if (this.jsonValidate.validate(this.dfschema) === false) {
      // assumes simple message - TBD???
      this.schemaMsg = this.jsonValidate.validateMsgs();
      if (this.validJSON) {
        this.jsonMsg = 'Enter a valid Schema';
        this.jsonErrMsgs = [];
      }
      return;
    }
    const pschema = JSON.parse(this.dfschema);
    if (!pschema.hasOwnProperty('jsonschema')) {
      this.schemaMsg = 'Invalid Schema - must specify jsonschema';
      if (this.validJSON) {
        this.jsonMsg = 'Enter a valid Schema';
        this.jsonErrMsgs = [];
      }
      return;
    }
    const jsonSchema = pschema.jsonschema;
    if (jsonSchema.hasOwnProperty('$schema')) {
      try {
        if (!(jsonSchema.$schema === 'http://json-schema.org/draft-04/schema#')  ) {
          this.schemaMsg = 'Invalid JSON Schema Data Format -  jsonschema$schema version must be 04';
          if (this.validJSON) {
            this.jsonMsg = 'Enter a Valid Schema';
            this.jsonErrMsgs = [];
          }
          return;
        }
      } catch(schemaVersionErr) {
         this.schemaMsg = 'Invalid JSON Schema Data Format -  jsonschema$schema version must be 04';
         if (this.validJSON) {
           this.jsonMsg = 'Enter a Valid Schema';
           this.jsonErrMsgs = [];
         }
         return;
      }
    } else {
       this.schemaMsg = 'Invalid JSON Schema Data Format -  jsonschema$schema must specified';
       if (this.validJSON) {
          this.jsonMsg = 'Enter a Valid Schema';
          this.jsonErrMsgs = [];
       }
       return;
    }
    if (this.validateMetaSchema.validate(this.dfschema) === false) {
      this.schemaMsg = 'Invalid Data Format Schema';
      this.schemaErrMsgs = this.validateMetaSchema.validateMsgs();
      if (this.validJSON) {
        this.jsonMsg = 'Enter a valid Schema';
        this.jsonErrMsgs = [];
      }
    } else {
      this.schemaMsg = 'Valid Data Format Schema';
      this.validSchema = true;
      if (this.validJSON ) {
        this.validateJSON();
      }
    }
  }

 // no reuse - so no service
 validateJSON() {
      this.jsonErrMsgs = [];
      this.jsonMsg = '';
      this.validJSON = false;
      if (this.dfjson.length == 0) {
        return;
      }
      if (this.jsonValidate.validate(this.dfjson) === false) {
        this.jsonMsg = this.jsonValidate.validateMsgs();
        this.jsonErrMsgs = [];
        return;
      }
      this.validJSON = true;
      if (!this.validSchema) {
        this.jsonMsg = 'Enter a Valid Schema';
        this.jsonErrMsgs = [];
        return;
      }
      // check for jsonschema in Schema file and validate based on version
      const valpschema = JSON.parse(this.dfschema);
      const valjsonSchema = valpschema.jsonschema;
      const schemaVersion = valjsonSchema.$schema;

      try {
        if (schemaVersion === 'http://json-schema.org/draft-04/schema#') {
          this.ajvService = new Ajv({
            meta: false, // optional, to prevent adding draft-06 meta-schema
            extendRefs: true, // optional, current default is to 'fail', spec behaviour is to 'ignore'
            allErrors:        true,
            unknownFormats: 'ignore'  // optional, current default is true (fail)
        });
        // change this to http get at some point TBD
        const schemav4: any = {    'id': 'http://json-schema.org/draft-04/schema#',    '$schema': 'http://json-schema.org/draft-04/schema#',    'description': 'Core schema meta-schema',    'definitions': {        'schemaArray': {            'type': 'array',            'minItems': 1,            'items': { '$ref': '#' }   },        'positiveInteger': {  'type': 'integer',            'minimum': 0        },        'positiveIntegerDefault0': {            'allOf': [ { '$ref': '#/definitions/positiveInteger' }, { 'default': 0 } ]        },        'simpleTypes': {            'enum': [ 'array', 'boolean', 'integer', 'null', 'number', 'object', 'string' ]        },        'stringArray': {            'type': 'array',            'items': { 'type': 'string' },            'minItems': 1,            'uniqueItems': true        }    },    'type': 'object',    'properties': {        'id': {            'type': 'string',            'format': 'uri'        },        '$schema': {            'type': 'string',            'format': 'uri'        },        'title': {            'type': 'string'        },        'description': {            'type': 'string'        },        'default': {},        'multipleOf': {            'type': 'number',            'minimum': 0,            'exclusiveMinimum': true        },        'maximum': {            'type': 'number'        },        'exclusiveMaximum': {            'type': 'boolean',            'default': false        },        'minimum': {            'type': 'number'        },        'exclusiveMinimum': {            'type': 'boolean',            'default': false        },        'maxLength': { '$ref': '#/definitions/positiveInteger' },        'minLength': { '$ref': '#/definitions/positiveIntegerDefault0' },        'pattern': {            'type': 'string',            'format': 'regex'        },        'additionalItems': {            'anyOf': [                { 'type': 'boolean' },                { '$ref': '#' }            ],            'default': {}        },        'items': {            'anyOf': [                { '$ref': '#' },                { '$ref': '#/definitions/schemaArray' }            ],            'default': {}        },        'maxItems': { '$ref': '#/definitions/positiveInteger' },        'minItems': { '$ref': '#/definitions/positiveIntegerDefault0' },        'uniqueItems': {            'type': 'boolean',            'default': false        },        'maxProperties': { '$ref': '#/definitions/positiveInteger' },        'minProperties': { '$ref': '#/definitions/positiveIntegerDefault0' },        'required': { '$ref': '#/definitions/stringArray' },        'additionalProperties': {            'anyOf': [                { 'type': 'boolean' },                { '$ref': '#' }            ],            'default': {}        },        'definitions': {            'type': 'object',            'additionalProperties': { '$ref': '#' },            'default': {}        },        'properties': {            'type': 'object',            'additionalProperties': { '$ref': '#' },            'default': {}        },        'patternProperties': {            'type': 'object',            'additionalProperties': { '$ref': '#' },            'default': {}        },        'dependencies': {            'type': 'object',            'additionalProperties': {                'anyOf': [                    { '$ref': '#' },                    { '$ref': '#/definitions/stringArray' }                ]            }        },        'enum': {            'type': 'array',            'minItems': 1,            'uniqueItems': true        },        'type': {            'anyOf': [                { '$ref': '#/definitions/simpleTypes' },                {                    'type': 'array',                    'items': { '$ref': '#/definitions/simpleTypes' },                    'minItems': 1,                    'uniqueItems': true                }            ]        },        'allOf': { '$ref': '#/definitions/schemaArray' },        'anyOf': { '$ref': '#/definitions/schemaArray' },        'oneOf': { '$ref': '#/definitions/schemaArray' },        'not': { '$ref': '#' }    },    'dependencies': {        'exclusiveMaximum': [ 'maximum' ],        'exclusiveMinimum': [ 'minimum' ]    },    'default': {}}

        const metaSchema = schemav4;

          this.ajvService.addMetaSchema(metaSchema);
          this.ajvService._opts.defaultMeta = metaSchema.id;

          // Optionally you can also disable keywords defined in draft-06
          this.ajvService.removeKeyword('propertyNames');
          this.ajvService.removeKeyword('contains');
          this.ajvService.removeKeyword('const');

        } else {
          this.jsonMsg = 'Invalid JSON Schema Data Format -  jsonschema$schema version must be 04';
          this.jsonErrMsgs = [];
          return;
        }
      } catch (ajvErrMsg) {

        this.jsonMsg = 'Failed - Schema checking initialization: ' + ajvErrMsg;
        this.jsonErrMsgs = [];
        return;
      }


      try {
        const pschema = JSON.parse(this.dfschema);
        const jsonSchema = pschema.jsonschema;

        const sValidate = this.ajvService.compile(jsonSchema);
        const result = sValidate(JSON.parse(this.dfjson));

        let j = 0;
        if (result === false) {
          for ( const errMsg of Object.keys(sValidate.errors)) {
             let msg = sValidate.errors[errMsg].message;
             if (sValidate.errors[errMsg].hasOwnProperty('params')) {
               if (sValidate.errors[errMsg].params.hasOwnProperty('additionalProperty')) {
                 msg = msg + ' - ';
                 msg = msg + sValidate.errors[errMsg].params.additionalProperty;
               }
             }
             let dupMsg = false;
             for (const k in this.jsonErrMsgs) {
               if ( this.jsonErrMsgs[k] === msg) {
                 dupMsg = true;
               }
             }
             if (dupMsg ===  false) {
              this.jsonErrMsgs[j] = msg;
              j = j + 1;
             }
          }
          this.jsonMsg = 'JSON Input does not match Schema:';
          return;
        }
      } catch (schemaError) {
        this.jsonMsg = 'Unexpected Schema Validation Error' + schemaError;
        return;
      }
      this.jsonMsg = 'JSON Input Validated';
      this.jsonErrMsgs = [];
  }

  doDFJSONChange(ev: any) {
      this.dfjson = ev.target.value;
      this.validateJSON();
  }
}
