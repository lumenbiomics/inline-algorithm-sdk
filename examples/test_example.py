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

Example file illustrating use of the InlineAlgoQueueProcessor base class
'''
from inline_algorithm.inline_algo_queue_processor import InlineAlgoQueueProcessor

class TestChild(InlineAlgoQueueProcessor):
    '''
    Example child class of InlineAlgoQueueProcessor
    '''
    def process(self, message):
        '''
        Method for processing incoming message from the scanner.
        '''
        print(f'Incoming message: {message}')
        return [[1, 2, 1, 'test_output']]

if __name__== '__main__':
    obj = TestChild(8000, 'localhost', docker_mode=False)
    obj.run()
