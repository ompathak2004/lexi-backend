from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date


class CaseSearchRequest(BaseModel):
    """Base request model for case searches"""
    
    state: str = Field(..., description="State name (e.g., 'GUJARAT')")
    commission: str = Field(..., description="Commission name (e.g., 'Ahmedabad City')")
    search_value: str = Field(..., description="Search value (case number, name, etc.)")
    from_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    to_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    page: Optional[int] = Field(0, ge=0, description="Page number (0-indexed)")
    size: Optional[int] = Field(30, ge=1, le=100, description="Page size")
    
    @field_validator('state', 'commission', 'search_value')
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Remove leading/trailing whitespace"""
        return v.strip()
    
    @field_validator('from_date', 'to_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format"""
        if v is None:
            return None
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "GUJARAT",
                "commission": "Ahmedabad City",
                "search_value": "Reddy",
                "from_date": "2025-01-01",
                "to_date": "2025-09-30",
                "page": 0,
                "size": 30
            }
        }


class IndustryTypeSearchRequest(BaseModel):
    """Request for searching by industry type"""
    
    state: str = Field(..., description="State name")
    commission: str = Field(..., description="Commission name")
    category_name: Optional[str] = Field(None, description="Industry category name (e.g., 'BANKING')")
    category_id: Optional[int] = Field(None, description="Industry category ID")
    from_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    to_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    page: Optional[int] = Field(0, ge=0)
    size: Optional[int] = Field(30, ge=1, le=100)
    
    @field_validator('from_date', 'to_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "GUJARAT",
                "commission": "Ahmedabad City",
                "category_name": "BANKING",
                "from_date": "2025-01-01",
                "to_date": "2025-09-30"
            }
        }


class JudgeSearchRequest(BaseModel):
    """Request for searching by judge"""
    
    state: str = Field(..., description="State name")
    commission: str = Field(..., description="Commission name")
    judge_name: Optional[str] = Field(None, description="Judge name")
    judge_id: Optional[int] = Field(None, description="Judge ID")
    from_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    to_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    page: Optional[int] = Field(0, ge=0)
    size: Optional[int] = Field(30, ge=1, le=100)
    
    @field_validator('from_date', 'to_date')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "GUJARAT",
                "commission": "Ahmedabad City",
                "judge_name": "M.H.PATEL",
                "from_date": "2025-01-01",
                "to_date": "2025-09-30"
            }
        }