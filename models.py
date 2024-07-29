from pydantic import BaseModel

class ScanStart(BaseModel):
    algorithm_id: str
    slide_name: str
    stain_name: str
    organ_name: str
    tile_width: int
    tile_height: int
    path_to_output: str

class ScanOngoing(BaseModel):
    slide_name: str
    tile_name: str
    tile_image_path: str
    row_idx: int
    col_idx: int

class ScanEnd(BaseModel):
    slide_name: str

class ScanAbort(BaseModel):
    slide_name: str