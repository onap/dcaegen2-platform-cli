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

import 'ajv';
import 'hammerjs';

import { AppComponent } from './app.component';
import { DFSchemaComponent } from './df-schema.component';
import { DFJSONInputComponent } from './df-jsoninput.component';
import { DFControlComponent } from './df-control.component';
import {ValidateMetaSchemaService} from './validate-metaschema.service';
import {ValidateJSONService} from './validate-json.service';
import {MetaSchemaService} from './metaschema.service';

const dfroutes: Routes = [
  { path: '', redirectTo: 'schemaval', pathMatch: 'full' },
  { path: 'schemaval',  component: DFSchemaComponent },
  { path: 'jsoninput',  component: DFJSONInputComponent },

];
@NgModule({
  imports:      [  BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    HttpModule,
    ReactiveFormsModule,
    FlexLayoutModule,
    RouterModule.forRoot(dfroutes),
    MaterialModule,
    ],
  declarations: [ AppComponent,
                  DFSchemaComponent,
                  DFJSONInputComponent,
                  DFControlComponent
                 ],
 providers: [
  ValidateMetaSchemaService,
  ValidateJSONService,
  MetaSchemaService
],
  bootstrap:    [ AppComponent ]
})
export class AppModule { }
