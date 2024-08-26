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

FastAPI server
'''

import os
import configparser
from threading import  Thread, Event
from queue import Queue

import uvicorn
from fastapi import FastAPI, Request

from models_scanner import TileResults, AlgorithmCompleted
from scanner_service_helpers import api_call_handler_scanner

my_path = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(my_path, "../config.ini")
config = configparser.ConfigParser()
config.read(config_path)
base_path=config.get('DEFAULT', 'BASE_PATH')
input_file_name=config.get('DEFAULT', 'INPUT_FILE_NAME')

app = FastAPI()
app.state.api_call_queue = Queue()

error_event = Event()
thread_handle = Thread(
       target=api_call_handler_scanner,
       args=(app.state.api_call_queue, base_path, input_file_name, error_event),
       daemon=True,
   )
thread_handle.start()

@app.post('/v1/tile-results', status_code=204)
async def tile_results(
        params: TileResults,
        request: Request
    ):
    app.state.api_call_queue.put(params)
    return "v1/tile-results received"

@app.post('/v1/algorithm-completed', status_code=204)
async def algorithm_completed(
        params: AlgorithmCompleted,
        request: Request
    ):
    app.state.api_call_queue.put(params)
    return "v1/algorithm-completed received"

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8001,
    )
