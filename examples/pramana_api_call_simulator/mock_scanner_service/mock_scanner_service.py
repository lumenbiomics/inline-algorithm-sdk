from fastapi import FastAPI, Request
import uvicorn
from models_scanner import TileResults, AlgorithmCompleted
from queue import Queue
import os
from threading import  Thread, Event
from scanner_service_helpers import api_call_handler_scanner
import configparser

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