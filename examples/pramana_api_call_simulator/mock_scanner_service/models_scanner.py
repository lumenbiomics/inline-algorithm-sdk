'''
Models used for the simulator
'''
from pydantic import BaseModel

class TileResults(BaseModel):
    '''
    Model for TileResults messages
    '''
    algorithm_id: str
    slide_name: str
    tile_name: str
    results: dict

class AlgorithmCompleted(BaseModel):
    '''
    Model for AlgorithmCompleted messages
    '''
    algorithm_id: str
    slide_name: str
