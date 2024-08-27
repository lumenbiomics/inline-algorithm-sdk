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

An implementation of the AbstractInlineAlgorithm to run within a FastAPI server 
and utilizing a queue to manage events.
'''
import json
from contextlib import asynccontextmanager
from queue import Queue
from threading import Thread, Event
import requests
from fastapi import FastAPI, Request, APIRouter, Response
import uvicorn
from .abstract_inline_algorithm import AbstractInlineAlgorithm
from .models import ScanStart, ScanOngoing, ScanEnd, ScanAbort, Results, TileResults


class InlineAlgoQueueProcessor(AbstractInlineAlgorithm):
    '''
    InlineAlgoQueueProcessor is an implementation of the AbstractInlineAlgorithm
    designed to run within a FastAPI application. It initializes necessary
    parameters such as port, host, and docker mode, and sets up a queue and
    an error event for managing a task that will read messages populated in a queue.

    Attributes:
        port (int): The port number the FastAPI app will run on.
        host (str): The host address the FastAPI app will bind to.
        docker_mode (bool): A flag indicating if the application is running in Docker mode.
        app (FastAPI): The FastAPI application instance.
        __queue (Queue): A queue to manage API messages.
        __error_event (Event): An event to handle error states.
        __router (APIRouter): The FastAPI router for handling routes.
    '''

    def __init__(self, port, host, docker_mode=True):
        self.port = port
        self.host = host
        self.docker_mode = docker_mode
        self.__queue = Queue()
        self.__error_event = Event()
        self.app = FastAPI(lifespan=self.lifespan)
        self.__router = APIRouter()
        self.__init_routes()

    def __init_routes(self):
        self.__router.add_api_route("/v1/scan/start", self.scan_start, methods=["PUT"])
        self.__router.add_api_route("/v1/scan/end", self.scan_end, methods=["PUT"])
        self.__router.add_api_route(
            "/v1/scan/image-tile", self.scan_ongoing, methods=["POST"]
        )
        self.__router.add_api_route("/v1/scan/abort", self.scan_abort, methods=["PUT"])
        self.app.include_router(self.__router)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        '''
        Manages the lifespan of the FastAPI application, ensuring that the
        API call handler loop runs in a separate thread during the server's 
        lifetime. The server start and end hooks are also called at appropriate
        times.  self.on_server_start() will be called on the FastAPI application 
        startup and self.on_server_end() will be called when the FastAPI application 
        gracefully shutdown

        Args:
            app (FastAPI): The FastAPI application instance.

        Yields:
            None: This context manager does not yield any values.
        '''
        thread_handle = Thread(
            target=self.api_call_handler_loop,
            daemon=True,
        )
        thread_handle.start()
        self.on_server_start()
        yield
        self.on_server_end()

    async def scan_start(self, params: ScanStart, request: Request):
        '''
        Handles the /v1/scan/start API endpoint. This method enqueues the provided
        scan parameters for processing and returns a response indicating the
        request was successfully received.

        Args:
            params (ScanStart): The request body for /v1/scan/start.
            request (Request): The incoming HTTP request.

        Returns:
            Response: A response object with status code 200.
        '''
        self.__queue.put(params)
        return Response(status_code=200)

    async def scan_ongoing(self, params: ScanOngoing, request: Request):
        '''
        Handles the /v1/scan/image-tile API endpoint. This method enqueues the provided
        scan parameters for processing and returns a response indicating the
        request was successfully received.

        Args:
            params (ScanOngoing): The request body for /v1/scan/image-tile.
            request (Request): The incoming HTTP request.

        Returns:
            Response: A response object with status code 202.
        '''
        self.__queue.put(params)
        return Response(status_code=202)

    async def scan_end(self, params: ScanEnd, request: Request):
        '''
        Handles the /v1/scan/end API endpoint. This method enqueues the provided
        scan parameters for processing and returns a response indicating the
        request was successfully received.

        Args:
            params (ScanEnd): The request body for /v1/scan/end.
            request (Request): The incoming HTTP request.

        Returns:
            Response: A response object with status code 204.
        '''
        self.__queue.put(params)
        return Response(status_code=204)

    async def scan_abort(self, params: ScanAbort, request: Request):
        '''
        Handles the /v1/scan/abort API endpoint. This method enqueues the provided
        scan parameters for processing and returns a response indicating the
        request was successfully received.

        Args:
            params (ScanAbort): The request body for /v1/scan/abort.
            request (Request): The incoming HTTP request.

        Returns:
            Response: A response object with status code 204.
        '''
        self.__queue.put(params)
        return Response(status_code=204)

    def api_call_handler_loop(self):
        '''
        Continuously handles API calls by processing messages from the queue.
        Depending on the type of message, it performs the corresponding action such
        as starting a scan, processing ongoing scan data, ending a scan, or aborting a scan.
        It also sends appropriate HTTP requests to specified URLs to communicate the results
        or status updates.

        This method runs in an infinite loop until an exception occurs, setting an error
        event if an exception is raised.

        Message Types:
            - ScanStart: Triggers the `on_scan_start` method.
            - ScanOngoing: Processes tile data and sends results to a specific URL.
            - ScanEnd: Sends a completion signal to a specific URL and triggers the
                       `on_scan_end` method.
            - ScanAbort: Triggers the `on_scan_abort` method.

        Exceptions:
            Any exception that occurs will set the error event and re-raise the exception.

        Raises:
            BaseException: Any exception encountered during the loop execution.
        '''
        try:
            while True:
                message = self.__queue.get()
                if isinstance(message, ScanStart):
                    algorithm_id = message.algorithm_id
                    slide_name = message.slide_name
                    self.on_scan_start(message)
                elif isinstance(message, ScanOngoing):
                    slide_name = message.slide_name
                    tile_name = message.tile_name
                    row_idx = message.row_idx
                    col_idx = message.col_idx
                    model_results = self.process(message)
                    results_dict = {
                        "row_idx": row_idx,
                        "col_idx": col_idx,
                        "detection_array": model_results,
                    }
                    results = Results(**results_dict)
                    data_json = {
                        "algorithm_id": algorithm_id,
                        "slide_name": slide_name,
                        "tile_name": tile_name,
                        "results": results.dict(),
                    }
                    tile_results = TileResults(**data_json)
                    tile_results_dict = tile_results.dict()
                    hostname = (
                        "host.docker.internal" if self.docker_mode else "localhost"
                    )
                    url = f"http://{hostname}:8001/v1/tile-results"
                    requests.post(url, data=json.dumps(tile_results_dict), timeout=1)
                elif isinstance(message, ScanEnd):
                    data_json = {"algorithm_id": algorithm_id, "slide_name": slide_name}
                    hostname = (
                        "host.docker.internal" if self.docker_mode else "localhost"
                    )
                    url = f"http://{hostname}:8001/v1/algorithm-completed"
                    requests.post(url, data=json.dumps(data_json), timeout=1)
                    self.on_scan_end(message)
                elif isinstance(message, ScanAbort):
                    algorithm_id = ""
                    slide_name = ""
                    self.on_scan_abort(message)

        except BaseException as e:
            self.__error_event.set()
            raise e

    def run(self):
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
        )

    def on_server_start(self):
        pass

    def on_server_end(self):
        pass

    def on_scan_start(self, message):
        pass

    def process(self, message):
        pass

    def on_scan_end(self, message):
        pass

    def on_scan_abort(self, message):
        pass
