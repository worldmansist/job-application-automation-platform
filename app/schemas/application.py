from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    status: str = "new"
    source: str = "telegram"


class ApplicationUpdate(BaseModel):
    company: str | None = None
    position: str | None = None
    status: str | None = None
    source: str | None = None


class ApplicationRead(BaseModel):
    id: int
    company: str
    position: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime