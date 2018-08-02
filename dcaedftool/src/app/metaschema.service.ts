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

@Injectable()
export class MetaSchemaService {

  private metaschemaVersions: string [] = ['1.0','1.1 test only'];
  private metaschemaVersion: string;

  //    Get it from a external URL?  Note version 6 now.
  private metaschema1_obj: any ={'$schema': 'http://json-schema.org/draft-04/schema#','title':'Data format specification schema Version 1.0','type':'object','oneOf':[{'properties':{'self':{'$ref':'#/definitions/self'},'dataformatversion':{'$ref':'#/definitions/dataformatversion'},'reference':{'type':'object','description':'A reference to an external schema','properties':{'name':{'$ref':'#/definitions/name'},'version':{'$ref':'#/definitions/version'},'format':{'$ref':'#/definitions/format'}},'required':['name','version','format'],'additionalProperties':false}},'required':['self','dataformatversion','reference'],'additionalProperties':false},{'properties':{'self':{'$ref':'#/definitions/self'},'dataformatversion':{'$ref':'#/definitions/dataformatversion'},'jsonschema':{'$schema':'http://json-schema.org/draft-04/schema#','description':'The JSON schema for this data format'}},'required':['self','dataformatversion','jsonschema'],'additionalProperties':false},{'properties':{'self':{'$ref':'#/definitions/self'},'dataformatversion':{'$ref':'#/definitions/dataformatversion'},'delimitedschema':{'type':'object','description':'A JSON schema for delimited files','properties':{'delimiter':{'enum':[',','|','\t']},'fields':{'type':'array','description':'Array of field descriptions','items':{'$ref':'#/definitions/field'}}},'additionalProperties':false}},'required':['self','dataformatversion','delimitedschema'],'additionalProperties':false},{'properties':{'self':{'$ref':'#/definitions/self'},'dataformatversion':{'$ref':'#/definitions/dataformatversion'},'unstructured':{'type':'object','description':'A JSON schema for unstructured text','properties':{'encoding':{'type':'string','enum':['ASCII','UTF-8','UTF-16','UTF-32']}},'additionalProperties':false}},'required':['self','dataformatversion','unstructured'],'additionalProperties':false}],'definitions':{'name':{'type':'string'},'version':{'type':'string','pattern':'^(\\d+\\.)(\\d+\\.)(\\*|\\d+)$'},'self':{'description':'Identifying Information','type':'object','properties':{'name':{'$ref':'#/definitions/name'},'version':{'$ref':'#/definitions/version'},'description':{'type':'string'}},'required':['name','version'],'additionalProperties':false},'format':{'description':'Referenceschematype','type':'string','enum':['JSON','DelimitedFormat','XML','Unstructured']},'field':{'description':'Afielddefinitionforthedelimitedschema','type':'object','properties':{'name':{'type':'string'},'description':{'type':'string'},'fieldtype':{'description':'the field type; XML schema types','type':'string','enum':['string','boolean','decimal','float','double','duration','dateTime','time','date','gYearMonth','gYear','gMonthDay','gDay','gMonth','hexBinary','base64Binary','anyURI','QName','NOTATION','normalizedString','token','language','IDREFS','ENTITIES','NMTOKEN','NMTOKENS','Name','NCName','ID','IDREF','ENTITY','integer','nonPositiveInteger','negativeInteger','long','int','short','byte','nonNegativeInteger','unsignedLong','unsignedInt','unsignedShort','unsignedByte','positiveInteger']},'fieldPattern':{'description':'Regular expression','type':'integer'},'fieldMaxLength':{'description':'The maximum length','type':'integer'},'fieldMinLength':{'description':'The minimum length','type':'integer'},'fieldMinimum':{'description':'The minimum numeric value','type':'integer'},'fieldMaximum':{'description':'The maximum numeric value','type':'integer'}},'additionalProperties':false},'dataformatversion':{'type':'string','enum':['1.0.0']}}};

  private currentMetaSchemaVersion = '1.0';

  constructor() {
  }

  currentMetaSchema(): any {
      return this.metaschema1_obj;
  }
  currentMetaSchemaFormatted(): string {
      return JSON.stringify(this.metaschema1_obj, undefined, '\t');
  }

  metaSchemaVersion(): string {
     return this.currentMetaSchemaVersion;
  }

  setMetaSchemaVersion(newVersion: string): boolean {
    this.currentMetaSchemaVersion = newVersion;
    return true;
  }

  metaSchemaVersions(): any {
    return this.metaschemaVersions;
  }

}
