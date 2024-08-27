'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.

---

This is an abstract base class from which other custom implementations can be derived.
'''

from abc import ABC, abstractmethod

class AbstractInlineAlgorithm(ABC):
    '''
    Abstract Base Class containing methods to use for building the inline
    algorithm container
    '''
    @abstractmethod
    def run(self):
        '''
        To start the API server
        '''
        pass

    @abstractmethod
    def on_server_start(self):
        '''
        To run when the API server starts up
        '''
        pass

    @abstractmethod
    def on_server_end(self):
        '''
        To run when the API server shuts down
        '''
        pass

    @abstractmethod
    def on_scan_start(self, message):
        '''
        Method to run when a scan starts
        '''
        pass

    @abstractmethod
    def process(self, message):
        '''
        Method to run when an AOI or tile is presented
        '''
        pass

    @abstractmethod
    def on_scan_end(self, message):
        '''
        Method to run when a scan ends
        '''
        pass

    @abstractmethod
    def on_scan_abort(self, message):
        '''
        Method to run when a scan aborts
        '''
        pass
