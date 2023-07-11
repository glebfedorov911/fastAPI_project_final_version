from pydantic import BaseModel

class PostCreate(BaseModel):
    head: str
    description: str

class PostUpdate(PostCreate):
    pass