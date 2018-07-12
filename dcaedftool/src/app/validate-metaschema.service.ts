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
import {MetaSchemaService} from './metaschema.service';
import {ValidateJSONService} from './validate-json.service';
import * as Ajv from 'ajv';

@Injectable()
export class ValidateMetaSchemaService {

  private ajv: any;
  private schemaValidate: any;
  private metaSchema: MetaSchemaService;
  private jsonValidate: ValidateJSONService;
  private lastErrors:string[] = [];

  constructor(metaSchemaService: MetaSchemaService, jsonValidateService: ValidateJSONService) {
    this.metaSchema = metaSchemaService;
    this.jsonValidate = jsonValidateService;
    }

  validate(schema: string): boolean {
     // check JSON
     if (this.jsonValidate.validate(schema) === false) {
       // assumes simple message - TBD???
       this.lastErrors[0] = this.jsonValidate.validateMsgs();
       return false;
     }
    // Schema is assumed to be V4 for now (jsonschema does not support V6 yet so we must wait since this is used by the CLI)
    try {
       this.ajv = new Ajv({
         meta: false, // optional, to prevent adding draft-06 meta-schema
         extendRefs: true, // optional, current default is to 'fail', spec behaviour is to 'ignore'
         allErrors:        true,
         unknownFormats: 'ignore'  // optional, current default is true (fail)
     });
     // change this to http get at some point TBD
     const schemav4: any = {    'id': 'http://json-schema.org/draft-04/schema#',    '$schema': 'http://json-schema.org/draft-04/schema#',    'description': 'Core schema meta-schema',    'definitions': {        'schemaArray': {            'type': 'array',            'minItems': 1,            'items': { '$ref': '#' }   },        'positiveInteger': {  'type': 'integer',            'minimum': 0        },        'positiveIntegerDefault0': {            'allOf': [ { '$ref': '#/definitions/positiveInteger' }, { 'default': 0 } ]        },        'simpleTypes': {            'enum': [ 'array', 'boolean', 'integer', 'null', 'number', 'object', 'string' ]        },        'stringArray': {            'type': 'array',            'items': { 'type': 'string' },            'minItems': 1,            'uniqueItems': true        }    },    'type': 'object',    'properties': {        'id': {            'type': 'string',            'format': 'uri'        },        '$schema': {            'type': 'string',            'format': 'uri'        },        'title': {            'type': 'string'        },        'description': {            'type': 'string'        },        'default': {},        'multipleOf': {            'type': 'number',            'minimum': 0,            'exclusiveMinimum': true        },        'maximum': {            'type': 'number'        },        'exclusiveMaximum': {            'type': 'boolean',            'default': false        },        'minimum': {            'type': 'number'        },        'exclusiveMinimum': {            'type': 'boolean',            'default': false        },        'maxLength': { '$ref': '#/definitions/positiveInteger' },        'minLength': { '$ref': '#/definitions/positiveIntegerDefault0' },        'pattern': {            'type': 'string',            'format': 'regex'        },        'additionalItems': {            'anyOf': [                { 'type': 'boolean' },                { '$ref': '#' }            ],            'default': {}        },        'items': {            'anyOf': [                { '$ref': '#' },                { '$ref': '#/definitions/schemaArray' }            ],            'default': {}        },        'maxItems': { '$ref': '#/definitions/positiveInteger' },        'minItems': { '$ref': '#/definitions/positiveIntegerDefault0' },        'uniqueItems': {            'type': 'boolean',            'default': false        },        'maxProperties': { '$ref': '#/definitions/positiveInteger' },        'minProperties': { '$ref': '#/definitions/positiveIntegerDefault0' },        'required': { '$ref': '#/definitions/stringArray' },        'additionalProperties': {            'anyOf': [                { 'type': 'boolean' },                { '$ref': '#' }            ],            'default': {}        },        'definitions': {            'type': 'object',            'additionalProperties': { '$ref': '#' },            'default': {}        },        'properties': {            'type': 'object',            'additionalProperties': { '$ref': '#' },            'default': {}        },        'patternProperties': {            'type': 'object',            'additionalProperties': { '$ref': '#' },            'default': {}        },        'dependencies': {            'type': 'object',            'additionalProperties': {                'anyOf': [                    { '$ref': '#' },                    { '$ref': '#/definitions/stringArray' }                ]            }        },        'enum': {            'type': 'array',            'minItems': 1,            'uniqueItems': true        },        'type': {            'anyOf': [                { '$ref': '#/definitions/simpleTypes' },                {                    'type': 'array',                    'items': { '$ref': '#/definitions/simpleTypes' },                    'minItems': 1,                    'uniqueItems': true                }            ]        },        'allOf': { '$ref': '#/definitions/schemaArray' },        'anyOf': { '$ref': '#/definitions/schemaArray' },        'oneOf': { '$ref': '#/definitions/schemaArray' },        'not': { '$ref': '#' }    },    'dependencies': {        'exclusiveMaximum': [ 'maximum' ],        'exclusiveMinimum': [ 'minimum' ]    },    'default': {}}

     const metaSchema = schemav4;

       this.ajv.addMetaSchema(metaSchema);
       this.ajv._opts.defaultMeta = metaSchema.id;

       // Optionally you can also disable keywords defined in draft-06
       this.ajv.removeKeyword('propertyNames');
       this.ajv.removeKeyword('contains');
       this.ajv.removeKeyword('const');

       const sValidate = this.ajv.compile(this.metaSchema.currentMetaSchema());
       const result = sValidate(JSON.parse(schema));
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
            for (const k in this.lastErrors) {
              if ( this.lastErrors[k] === msg) {
                dupMsg = true;
              }
            }
            if (dupMsg ===  false) {
             this.lastErrors[j] = msg;
             j = j + 1;
            }
         }
       }
       return result;
    } catch(ajvError){
       this.lastErrors[0] =  ajvError;
    }
  }

  validateMsgs(): string[] {
    return this.lastErrors;
  }
}
