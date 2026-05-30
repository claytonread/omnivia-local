from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class MemoryCreate(BaseModel):
    content: str
    source: Optional[str] = None
    memory_type: Optional[str] = "general"
    created_by: Literal["human", "agent"] = "human"


class Memory(BaseModel):
    id: str
    content: str
    source: Optional[str]
    memory_type: str
    approval_status: Literal["proposed", "observed", "approved"]
    created_by: Literal["human", "agent"]
    created_at: datetime
    embedding_id: Optional[str] = None

    class Config:
        from_attributes = True


class MemorySearch(BaseModel):
    query: str
    limit: int = 5
    approval_status: Optional[str] = None