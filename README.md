# inline-algorithm-sdk

**SDK Documentation**: <a href="https://developers.pramana.ai/inline-algorithms/sdk/documentation" target="_blank">https://developers.pramana.ai/inline-algorithms/sdk/documentation</a>

**API Documentation**: <a href="https://developers.pramana.ai/inline-algorithms/documentation" target="_blank">https://developers.pramana.ai/inline-algorithms/documentation</a>

**Source Code**: <a href="https://github.com/lumenbiomics/inline-algorithm-sdk" target="_blank">https://github.com/lumenbiomics/inline-algorithm-sdk</a>

---

## Requirements

* Needs <a href="https://www.python.org/downloads/" class="external-link" target="_blank">Python3.10</a> or higher

---

## Installation

<div class="termy">

```console
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install inline_algorithm@git+https://github.com/lumenbiomics/inline-algorithm-sdk.git
```
</div>

---

## Example to run locally
* Create a file `main.py` with:
```python
from inline_algorithm.inline_algo_queue_processor import InlineAlgoQueueProcessor

class TestChild(InlineAlgoQueueProcessor):
    def __init__(self, port, host, docker_mode=True):
        super().__init__(port, host, docker_mode)

    #optional
    def on_server_start(self):
        print('loading model')
        return
    #optional
    def on_server_end(self):
        print('freeing memory')
        return
    
    #update this function with your machine learning model detection/segmentation helper
    def process(self, message):
        """
        Processes a message of type ScanOngoing.

        Parameters:
        -----------
        message : ScanOngoing
            An instance of the ScanOngoing class.

        The ScanOngoing class is defined as follows:
        -------------------------------------------
        class ScanOngoing(BaseModel):
            slide_name: str
                The name of the slide being scanned.
            tile_name: str
                The name of the tile within the slide.
            tile_image_path: str
                The file path to the image of the tile.
            row_idx: int
                The row index of the tile in the grid.
            col_idx: int
                The column index of the tile in the grid.

        Returns:
        --------
        List[DetectionArray]
            A list containing the processed data. Example:
                [
                    {"bbox": [0, 0, 1, 1], "confidence": 0.9, "class": "tumor"},
                    {"bbox": [123, 321, 278, 456], "confidence": 0.6, "class": "stroma"},
                ]
            The bounding box (bbox) value contains information about model detections in the
            form of [x1, y1, x2, y2].

            OR

        List[List] (to be deprecated in the future)
            A two-dimensional list with the processed data. Ex - [[0, 0, 0.9, 1.2, 0.8, "tumor"], [123, 321, 200, 400, 0.6, "stroma"]].
            Each sub array contains information about bounding boxes like [x1, y1, x2, y2, confidence, class strings].
        """
        return 
    

if __name__== '__main__':
    obj = TestChild(8000, 'localhost', docker_mode=False)
    obj.run()
```
* Run the server: ```python main.py```
* This will run the Fast API server and will be able to handle all the API requests
* You can test this example with the Pramana API call simulator which will simulate the Pramana scanner's scanning pipeline. See this [section](#test-with-the-simulator)


---
## Test with the simulator
* Clone this repository and follow the instructions in this <a href="https://github.com/lumenbiomics/inline-algorithm-sdk/tree/main/examples/pramana_api_call_simulator" class="external-link" target="_blank">README.md</a> to setup the simulator
```console
$ git clone https://github.com/lumenbiomics/inline-algorithm-sdk
```
* The simulator will emulate the Pramana scanner and simulate making API calls to port ```8000``` (as specified in the above example).
---
## Dockerize the Inline Algorithm
* Create a file called ```Dockerfile``` with these contents
```dockerfile
# Use the official Python image from Docker Hub
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND noninteractive
WORKDIR /app

RUN apt-get update

#Add any other files you need
COPY test.py  .
#COPY <your-requirements.txt-file> if any

# Install dependencies
RUN pip install inline_algorithm@git+https://github.com/lumenbiomics/inline-algorithm-sdk.git
# Install any other dependencies
#RUN pip install -r <your-requirements.txt-file> if any

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the application
CMD ["python3", "main.py"]
```
* Run the following command to build your Docker image:
```console
$ docker build -t <image name>:<tag> .
```
* Create a file called ```docker-compose.yml``` with these contents
```docker-compose
version: '3.9'
x-pramana-ui-name: Pramana Simulator
services:
  model:
    image: '<image name>:<tag>'
    volumes:
      - '<local basepath from your machine>/pramana_api_call_simulator/data:/data/acquired_data'
    ports:
      - '8000:8000'
    extra_hosts:
      - 'host.docker.internal:host-gateway'
```
Note: For the ```docker-compose.yml``` requirements that we need for the Inline Algorithm to run on the Pramana Scanner, please refer to the official API documentation <a href="https://developers.pramana.ai/inline-algorithms/documentation#section/Container-specifications" target="_blank">here</a>. In this example above, the ```volume``` mount and ```ports``` are specifically set to work with the simulator and **NOT** the Pramana Scanner.
* Turn on the container using this command : ```docker compose -f <path to the docker compose file> up ```
