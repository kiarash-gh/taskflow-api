from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: int = Field(default=3, ge=1, le=3)

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    priority: int
    completed: bool
    created_at: datetime


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: int | None = Field(default=None, ge=1, le=3)
    completed: bool | None = None