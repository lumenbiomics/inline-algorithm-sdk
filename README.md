# inline-algorithm-sdk

**Documentation**: <a href="https://developers.pramana.ai/inline-algorithms/documentation" target="_blank">https://developers.pramana.ai/inline-algorithms/documentation</a>

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

## Example
* Create a file `main.py` with:
```python
from inline_algorithm.inline_algo_queue_processor import InlineAlgoQueueProcessor

class TestChild(InlineAlgoQueueProcessor):
    def __init__(self, port, host, docker_mode=True):
        super().__init__(port, host, docker_mode)
    
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
            A two-dimensional list with the processed data. Ex - [[0, 0, 0.9, "tumor"], [123, 321, 0.6, "stroma"]]
        """
        return 
    
    #optional
    def on_server_start(self):
        print('loading model')
        return
    
    #optional
    def on_server_end(self):
        print('freeing memory')
        return

if __name__== '__main__':
    obj = TestChild(8000, 'localhost', docker_mode=False)
    obj.run()
```
---
## Test with Simulator
* Clone this repository and follow the instructions in this <a href="https://github.com/lumenbiomics/inline-algorithm-sdk/tree/main/examples/pramana_api_call_simulator" class="external-link" target="_blank">README.md</a> to setup the simulator
```console
$ git clone https://github.com/lumenbiomics/inline-algorithm-sdk
```
