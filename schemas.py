from pydantic import BaseModel
from typing import Optional


class TaskBase(BaseModel):
    title: str
    priority: str


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class Task(TaskBase):
    id: int
    status: str

    class Config:
        orm_mode = True
