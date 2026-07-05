from pydantic import BaseModel 

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class NoteCreate(BaseModel):
    title : str 
    content : str 

class NoteResponse(BaseModel):
    title: str
    content: str
    owner_id: int
