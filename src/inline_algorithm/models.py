'''
Defining Pydantic models
'''
from typing import List, Any
from pydantic import BaseModel

class ScanStart(BaseModel):
    '''
    For the /scan/start API message
    '''
    algorithm_id: str
    slide_name: str
    stain_name: str
    organ_name: str
    tile_width: int
    tile_height: int
    path_to_output: str

class ScanOngoing(BaseModel):
    '''
    For the /scan/image-tile API message
    '''
    slide_name: str
    tile_name: str
    tile_image_path: str
    row_idx: int
    col_idx: int

class ScanEnd(BaseModel):
    '''
    For the /scan/end API message
    '''
    slide_name: str

class ScanAbort(BaseModel):
    '''
    For the /scan/abort API message
    '''
    slide_name: str

class Results(BaseModel):
    '''
    For the final results of an algorithm
    '''
    detection_array: List[List[Any]]
    row_idx: int
    col_idx: int

class TileResults(BaseModel):
    '''
    For the results per tile of an algorithm
    '''
    algorithm_id: str
    slide_name: str
    tile_name: str
    results: dict
