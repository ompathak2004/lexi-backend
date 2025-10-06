from pydantic import BaseModel, Field
from typing import List, Optional


class StateResponse(BaseModel):
    """Response model for a single state"""
    
    commission_id: int
    commission_name: str
    is_circuit_bench: bool
    is_active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "commission_id": 11240000,
                "commission_name": "GUJARAT",
                "is_circuit_bench": False,
                "is_active": True
            }
        }


class CommissionResponse(BaseModel):
    """Response model for a single commission/district"""
    
    commission_id: int
    commission_name: str
    is_circuit_bench: bool
    is_active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "commission_id": 11240438,
                "commission_name": "Ahmedabad City",
                "is_circuit_bench": False,
                "is_active": True
            }
        }


class CategoryResponse(BaseModel):
    """Response model for industry category"""
    
    category_id: int
    category_name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "category_id": 43,
                "category_name": "BANKING"
            }
        }


class JudgeResponse(BaseModel):
    """Response model for judge"""
    
    judge_id: int
    judge_name: str
    commission_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "judge_id": 11446,
                "judge_name": "HON'BLE MR. President M.H.PATEL",
                "commission_id": 12240438
            }
        }


class CaseResponse(BaseModel):
    """Response model for a single case"""
    
    case_number: str
    case_stage: str
    filing_date: str
    complainant: str
    complainant_advocate: Optional[str] = None
    respondent: Optional[str] = None
    respondent_advocate: Optional[str] = None
    document_link: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_number": "DC/AB1/484/CC/21/344",
                "case_stage": "ALLOWED",
                "filing_date": "2021-12-28",
                "complainant": "SMT. DARSHANA MAHESH ROSHANKHEDE",
                "complainant_advocate": "ADV. LALIT LIMAYE",
                "respondent": "MAHARASHTRA STATE ELECTRICITY DISTRIBUTION",
                "respondent_advocate": "ADV. XYZ",
                "document_link": "base64_encoded_document"
            }
        }


class ErrorResponse(BaseModel):
    """Response model for API errors"""
    
    success: bool = False
    message: str
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "State 'INVALID_STATE' not found",
                "error": "StateNotFoundException"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    
    success: bool = False
    message: str
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Failed to fetch data",
                "error": "State not found"
            }
        }