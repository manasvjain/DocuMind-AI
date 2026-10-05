from datetime import datetime
from pydantic import BaseModel,Field
from app.models import JobStatus
class JobCreate(BaseModel):
    project_id:str; imagery_id:str; model_name:str=Field(default="unet",pattern="^(unet|deeplabv3plus|segformer)$"); model_version:str|None=None
class JobResponse(BaseModel):
    id:str; project_id:str; imagery_id:str; created_by:str; status:JobStatus; stage:str; progress:float; error:str|None; model_name:str; model_version:str|None; started_at:datetime|None; completed_at:datetime|None; created_at:datetime
    model_config={"from_attributes":True}
