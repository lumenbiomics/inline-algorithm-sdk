from AbstractInlineAlgorithmClass import AbstractInlineAlgorithmClass
from fastapi import FastAPI, Request, APIRouter
import uvicorn
import json
import time
import requests
from queue import Queue
from threading import  Thread, Event
from models import ScanStart, ScanOngoing, ScanEnd, ScanAbort

from helpers import model_detection_helper

class PramanaInlineAlgorithmClass(AbstractInlineAlgorithmClass, FastAPI):
    def __init__(self, port, host, model) -> None:
        self.port = port
        self.host = host
        self.queue = Queue()
        self.error_event = Event()
        self.model = model
        self.app = FastAPI()
        self.router = APIRouter()

        # Define endpoints
        @self.app.put('/v1/scan/start',status_code=200)
        async def scan_start(
        params: ScanStart,
        request: Request
    ):
            self.queue.put(params)
            return "v1/scan/start received"

        @self.app.post('/v1/scan/image-tile', status_code=202)
        async def scan_ongoing(
                params: ScanOngoing,
                request: Request
            ):
            self.queue.put(params)
            return "v1/scan/image-tile received"

        @self.app.put('/v1/scan/end', status_code=204)
        async def scan_end(
                params: ScanEnd,
                request: Request
            ):
            self.queue.put(params)
            return "v1/scan/end received"
        
        @self.app.put('/v1/scan/abort', status_code=204)
        async def scan_end(
                params: ScanAbort,
                request: Request
            ):
            self.queue.put(params)
            return "v1/scan/abort received"
    
    def __init_routes(self,):
        self.router.add_api_route('/v1/scan/start', scan_start, methods = ['PUT'])
        self.router.add_api_route('/v1/scan/end', scan_end, methods = ['PUT'])
        self.router.add_api_route('/v1/scan/image-tile/', scan_image_tile, methods = ['POST'])
        self.router.add_api_route('/v1/scan/abort', scan_abort, methods = ['PUT'])
        

    
    def on_server_start(self,):
        
        thread_handle = Thread(
       target=self.api_call_handler_loop,
    #    args=(app.state.api_call_queue, args.docker, error_event, model),
       daemon=True,
        )
        thread_handle.start()
    
    def api_call_handler_loop(self):
        try:
            while True:
                message = self.queue.get()
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
                    results = model_detection_helper(self.model, path)
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
                    url = 'http://localhost:8001/v1/tile-results'
                    # if is_running_as_docker:
                    #     url = 'http://host.docker.internal:8001/v1/tile-results'
                    requests.post(url, data = json.dumps(data_json), timeout=1)

                elif type(message) == ScanEnd:
                    data_json = {
                    "algorithm_id": algorithm_id,
                    "slide_name": slide_name
                    }
                    url = 'http://localhost:8001/v1/algorithm-completed'
                    # if is_running_as_docker:
                    #     url = 'http://host.docker.internal:8001/v1/algorithm-completed'
                    requests.post(url, data = json.dumps(data_json), timeout=1)
                    print('start end')
        except BaseException as e:
            self.error_event.set()
            raise e
    
    def run(self):
        self.on_server_start()
        uvicorn.run(
        self.app,
        host=self.host,
        port=self.port,
    )
    
    def on_server_end(self):
        print('on_server_end')
        return

    def on_scan_start(self):
        print("In on_scan_start")
        print(f"Time now : {time.time()}")
        return

    def process(self):
        print('process')
        print(f"Time now : {time.time()}")
        return

    def on_scan_end(self):
        print('on_scan_end')
        return

    def on_scan_abort(self):
        print('on_scan_abort')
        return


if __name__== '__main__':
    obj = PramanaInlineAlgorithmClass(8000, 'localhost', 'model')
    obj.run()

