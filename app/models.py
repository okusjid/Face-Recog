from pydantic import BaseModel

class TaskInput(BaseModel):
    name: str
