from pydantic import BaseModel,Field,field_validator
from app.models import Role

def validate_email_value(value:str)->str:
    value=value.strip().lower()
    if "@" not in value or value.startswith("@") or value.endswith("@") or value.count("@")!=1: raise ValueError("Enter a valid email address")
    local,domain=value.rsplit("@",1)
    if not local or "." not in domain or " " in value: raise ValueError("Enter a valid email address")
    return value
class RegisterRequest(BaseModel):
    email:str; full_name:str=Field(min_length=2,max_length=200); password:str=Field(min_length=8,max_length=128); role:Role=Role.VIEWER
    @field_validator("email")
    @classmethod
    def email_validator(cls,value): return validate_email_value(value)
class LoginRequest(BaseModel):
    email:str; password:str
    @field_validator("email")
    @classmethod
    def email_validator(cls,value): return validate_email_value(value)
class TokenResponse(BaseModel):
    access_token:str; refresh_token:str; token_type:str="bearer"
class RefreshRequest(BaseModel): refresh_token:str
class UserResponse(BaseModel):
    id:str; email:str; full_name:str; role:Role; is_active:bool
    model_config={"from_attributes":True}
