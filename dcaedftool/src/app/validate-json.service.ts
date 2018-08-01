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
export class ValidateJSONService {

  private lastErrors: string;


  constructor() {

    }

  validate( jsonString: string): boolean {
    try {
      // check for JSON validity
      const jsonTestObject = JSON.parse(jsonString);
      this.lastErrors = 'Valid JSON';
      return true;
    } catch (jsonErrMsg) {
      this.lastErrors = 'Invalid JSON: ' + jsonErrMsg;
      return false;
    }

  }
  validateMsgs(): string {
    return this.lastErrors;
  }


}