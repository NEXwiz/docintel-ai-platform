from pydantic import BaseModel
from datetime import datetime

class DocumentBase(BaseModel):
    filename:str

class DocumentCreate(DocumentBase):
    filename:str

class DocumentResponse(DocumentBase):
    id:int
    user_id:int
    status:str
    created_at:datetime

    class Config:
        orm_mode = True