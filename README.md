# inline-algorithm-sdk

**Documentation**: <a href="https://developers.pramana.ai/inline-algorithms/documentation" target="_blank">https://developers.pramana.ai/inline-algorithms/documentation</a>

**Source Code**: <a href="https://github.com/lumenbiomics/inline-algorithm-sdk" target="_blank">https://github.com/lumenbiomics/inline-algorithm-sdk</a>

---

## Requirements

FastAPI stands on the shoulders of giants:

* Needs <a href="https://www.python.org/downloads/" class="external-link" target="_blank">Python3.9</a> or higher

---

## Installation

<div class="termy">

```console
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install inline_algorithm@git+https://github.com/lumenbiomics/inline-algorithm-sdk.git@ISSUE-10903-sdk
```
</div>

---

## Example
* Create a file `main.py` with:
```python
from inline_algorithm.PramanaInlineAlgorithmClass import PramanaInlineAlgorithmClass

class TestChildClass(PramanaInlineAlgorithmClass):
    def __init__(self, port, host, docker_mode=True):
        super().__init__(port, host, docker_mode)
    
    def process(self, message):
        return [[1, 2, 1, 'test_output']]
    
    #optional
    def on_server_start(self):
        print('loading model')
        return
    
    #optional
    def on_server_end(self):
        print('freeing memory')
        return

if __name__== '__main__':
    obj = TestChildClass(8000, 'localhost', docker_mode=False)
    obj.run()
```
---
## Test with Simulator
* Clone this repository and follow the instructions in this <a href="https://github.com/lumenbiomics/inline-algorithm-sdk/tree/ISSUE-10903-sdk/examples/pramana_api_call_simulator" class="external-link" target="_blank">README.md</a> to setup the simulator
```console
$ git clone https://github.com/lumenbiomics/inline-algorithm-sdk
```