from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class SEUserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    first_name: str
    last_name: str
    grade_level: int = Field(ge=1, le=12)  # Grade level between 1 and 12
    group_ids: List[str]
    language: str
    preferred_type: str

class SEUserCreate(SEUserBase):
    pass

class SEUserUpdate(SEUserBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    grade_level: Optional[int] = Field(None, ge=1, le=12)
    group_ids: Optional[List[str]] = None
    language: Optional[str] = None
    preferred_type: Optional[str] = None

class SEUserResponse(SEUserBase):
    created_at: datetime 