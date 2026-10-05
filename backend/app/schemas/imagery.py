from datetime import datetime
from pydantic import BaseModel
class ImageryResponse(BaseModel):
    id:str; project_id:str; original_name:str; mime_type:str; size_bytes:int; width:int|None; height:int|None; bands:int|None; resolution_x:float|None; resolution_y:float|None; crs:str|None; bounds:dict|None; transform:dict|None; georeferenced:bool; is_demo:bool; created_at:datetime
    model_config={"from_attributes":True}
