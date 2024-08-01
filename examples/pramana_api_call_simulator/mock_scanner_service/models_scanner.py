from pydantic import BaseModel

class TileResults(BaseModel):
    algorithm_id: str
    slide_name: str
    tile_name: str
    results: dict

class AlgorithmCompleted(BaseModel):
    algorithm_id: str
    slide_name: str


