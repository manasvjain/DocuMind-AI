from datetime import datetime
from pydantic import BaseModel,Field
class ProjectCreate(BaseModel):
    village_name:str=Field(min_length=1,max_length=200); district:str; state:str; country:str="India"; latitude:float|None=None; longitude:float|None=None; crs:str|None=None; survey_date:datetime|None=None; description:str|None=None
class ProjectUpdate(BaseModel):
    village_name:str|None=None; district:str|None=None; state:str|None=None; country:str|None=None; latitude:float|None=None; longitude:float|None=None; crs:str|None=None; survey_date:datetime|None=None; description:str|None=None; processing_status:str|None=None; model_version:str|None=None
class ProjectResponse(BaseModel):
    id:str; owner_id:str; village_name:str; district:str; state:str; country:str; latitude:float|None; longitude:float|None; crs:str|None; survey_date:datetime|None; description:str|None; processing_status:str; model_version:str|None; created_at:datetime
    model_config={"from_attributes":True}
