Example
========


Running locally
---------------

To run a FastAPI server made with help from this package, we can do the following.

First, create a file ``main.py``.
In that file, add the following code:

.. code-block::

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
            List[List]
                A two-dimensional list with the processed data.
                    Ex - [[0, 0, 0.9, "tumor"], [123, 321, 0.6, "stroma"]]

                This 2D list should contain model detections where each sub array contains
                information about model detections like [x1, y1, confidence, class strings]
                for centroids or [x1, y1, x2, y2, confidence, class strings] for boundary boxes.
            """
            return
    
    
    if __name__== '__main__':
        obj = TestChild(8000, 'localhost', docker_mode=False)
        obj.run()

Run this server like so: ``python main.py``.
This will run the Fast API server and will be able to handle all the API requests.

Testing with a simulator
------------------------

Clone this repository and follow the instructions in this
`README <https://github.com/lumenbiomics/inline-algorithm-sdk/tree/main/examples/pramana_api_call_simulator>`_
to setup the simulator.

.. code-block::

    $ git clone https://github.com/lumenbiomics/inline-algorithm-sdk

Dockerizing your inline algorithm
---------------------------------

Create a file called ``Dockerfile`` with these contents.

.. code-block::

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

Run the following command to build your Docker image:

.. code-block::

    $ docker build -t <image name>:<tag> .

Create a file called ```docker-compose.yml``` with these contents

.. code-block::

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

Note: For the ``docker-compose.yml`` requirements that we need for the Inline Algorithm to run on
the Pramana Scanner, please refer to the official API documentation
`here <https://developers.pramana.ai/inline-algorithms/documentation#section/Container-specifications>`_.
In this example above, the ``volume`` mount and ``ports`` are specifically set to work with
the simulator and **NOT** the Pramana Scanner.

Turn on the container using this command: ``docker compose -f <path to the docker compose file> up``
