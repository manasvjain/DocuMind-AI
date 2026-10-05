from pydantic import BaseModel
class Message(BaseModel): message:str
class PageMeta(BaseModel): page:int; page_size:int; total:int
