from datetime import datetime
from pydantic import BaseModel,Field
class ModelResponse(BaseModel):
    id:str; name:str; version:str; architecture:str; training_dataset:str|None=None; classes:list|None=None; metrics:dict|None=None; checkpoint_location:str|None=None; status:str; is_demo:bool; created_at:datetime
    model_config={"from_attributes":True}
class ModelCreate(BaseModel):
    name:str=Field(min_length=1,max_length=100); version:str=Field(min_length=1,max_length=50); architecture:str=Field(min_length=1,max_length=100); training_dataset:str|None=Field(default=None,max_length=255); classes:list[str]=Field(default_factory=lambda:["background","building","road","water","vegetation","candidate parcel"]); metrics:dict|None=None; checkpoint_location:str|None=None; is_demo:bool=False
