"""
Pydantic Data Models & Request Schemas
=====================================
Provides data validation, automatic serialization, and interactive Swagger docs.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any


class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full Name")
    phone: str = Field(..., min_length=7, max_length=20, description="Phone number with country code")
    email: Optional[str] = Field(None, max_length=100, description="Email address")
    category: str = Field("General", description="Category: Friends, Work, College, Family, Emergency")
    company: Optional[str] = Field("", description="Company, Department, or University")
    notes: Optional[str] = Field("", description="Additional notes or tags")
    is_favorite: bool = Field(False, description="Starred as favorite contact")
    call_count: int = Field(0, ge=0, description="Frequency of interactions (for Max-Heap)")


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    category: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None
    call_count: Optional[int] = None


class ContactResponse(ContactBase):
    id: int
    created_at: Optional[str] = None


class RelationshipCreate(BaseModel):
    from_id: int
    to_id: int
    relationship: str = Field(..., description="e.g. Colleague, Batchmate, Friend, Family")


class ConnectionPathQuery(BaseModel):
    from_id: int
    to_id: int
