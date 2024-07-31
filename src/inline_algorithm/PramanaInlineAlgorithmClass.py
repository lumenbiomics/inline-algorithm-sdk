from fastapi import FastAPI, Request, APIRouter, Response
import uvicorn
from AbstractInlineAlgorithmClass import AbstractInlineAlgorithmClass
import json
import requests
from contextlib import asynccontextmanager
from queue import Queue
from threading import  Thread, Event
from models import ScanStart, ScanOngoing, ScanEnd, ScanAbort, Results, TileResults

class PramanaInlineAlgorithmClass(AbstractInlineAlgorithmClass):
    def __init__(self, port, host, docker_mode=True):
        self.port = port
        self.host = host
        self.docker_mode = docker_mode
        self.__queue = Queue()
        self.__error_event = Event()
        self.app = FastAPI(lifespan=self.lifespan)
        self.__router = APIRouter()
        self.__init_routes()
    
    def __init_routes(self,):
        self.__router.add_api_route('/v1/scan/start', self.scan_start, methods = ['PUT'])
        self.__router.add_api_route('/v1/scan/end', self.scan_end, methods = ['PUT'])
        self.__router.add_api_route('/v1/scan/image-tile', self.scan_ongoing, methods = ['POST'])
        self.__router.add_api_route('/v1/scan/abort', self.scan_abort, methods = ['PUT'])
        self.app.include_router(self.__router)
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        thread_handle = Thread(
       target=self.api_call_handler_loop,
       daemon=True,
        )
        thread_handle.start()
        self.on_server_start()
        yield
        self.on_server_end()
    
    
    async def scan_start(
            self,
            params: ScanStart,
            request: Request
        ):
        self.__queue.put(params)
        return Response(status_code=200)
    
    async def scan_ongoing(
        self,
        params: ScanOngoing,
        request: Request
    ):
        self.__queue.put(params)
        return Response(status_code=202)

    async def scan_end(
        self,
        params: ScanEnd,
        request: Request
    ):
        self.__queue.put(params)
        return Response(status_code=204)

    async def scan_abort(
        self,
        params: ScanAbort,
        request: Request
    ):
        self.__queue.put(params)
        return Response(status_code=204)

    def api_call_handler_loop(self):
        try:
            while True:
                message = self.__queue.get()
                if type(message) == ScanStart:
                    algorithm_id = message.algorithm_id
                    slide_name = message.slide_name
                    organ_name = message.organ_name
                    path_to_output = message.path_to_output
                    self.on_scan_start(message)                    
                elif type(message) == ScanOngoing:
                    path = message.tile_image_path
                    slide_name = message.slide_name
                    tile_name = message.tile_name
                    row_idx = message.row_idx
                    col_idx = message.col_idx
                    model_results = self.process(message)
                    results_dict = {
                        "row_idx": row_idx,
                        "col_idx": col_idx,
                        "detection_array": model_results
                    }
                    results = Results(**results_dict)
                    data_json = {
                        "algorithm_id": algorithm_id,
                        "slide_name": slide_name,
                        "tile_name": tile_name,
                        "results": {
                        "detection_array": results,
                        "row_idx": row_idx,
                        "col_idx": col_idx
                        }
                    }
                    tile_results = TileResults(**data_json) 
                    tile_results_dict = tile_results.dict()
                    url = 'http://localhost:8001/v1/tile-results'
                    if self.docker_mode:
                        url = 'http://host.docker.internal:8001/v1/tile-results'
                    requests.post(url, data = json.dumps(tile_results_dict), timeout=1)
                elif type(message) == ScanEnd:
                    data_json = {
                    "algorithm_id": algorithm_id,
                    "slide_name": slide_name
                    }
                    url = 'http://localhost:8001/v1/algorithm-completed'
                    if self.docker_mode:
                        url = 'http://host.docker.internal:8001/v1/algorithm-completed'
                    requests.post(url, data = json.dumps(data_json), timeout=1)
                    self.on_scan_end(message) 
                elif type(message) == ScanAbort:
                    algorithm_id = ''
                    slide_name = ''
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