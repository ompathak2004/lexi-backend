from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
import logging
from app.models.requests import CaseSearchRequest, IndustryTypeSearchRequest, JudgeSearchRequest
from app.models.responses import StateResponse, CommissionResponse, CategoryResponse, JudgeResponse, CaseResponse
from app.services.mapper_service import mapper_service
from app.services.case_service import case_service
from app.utils.exceptions import JagritiAPIException

router = APIRouter(prefix="/api/v1", tags=["Case Search"])
route_logger = logging.getLogger("app.routes")



@router.get(
    "/states",
    response_model=List[StateResponse],
    summary="Get all states",
    description="Retrieve list of all District Consumer Courts (DCDRC) states with their IDs"
)
async def get_states():
    """
    Get all available states/commissions.
    """
    route_logger.info("📍 GET /states - Fetching all available states")
    try:
        states = await mapper_service.get_all_states()
        route_logger.info(f"✅ GET /states - Returning {len(states)} states")
        return states
    except JagritiAPIException as e:
        route_logger.error(f"🚨 GET /states - Jagriti API error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        route_logger.error(f"💥 GET /states - Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/commissions/{state_id}",
    response_model=List[CommissionResponse],
    summary="Get commissions by state",
    description="Retrieve list of district commissions for a specific state"
)
async def get_commissions(state_id: int):
    """
    Get all district commissions for a state.
    
    Args:
        state_id: State commission ID
        
    Returns:
        List of district commissions. Empty list if state has no districts.
    """
    try:
        commissions = await mapper_service.get_commissions_by_state(state_id)
        return commissions
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/categories",
    response_model=List[CategoryResponse],
    summary="Get all industry categories",
    description="Retrieve list of all case categories/industry types"
)
async def get_categories():
    """Get all available case categories."""
    try:
        categories = await mapper_service.get_all_categories()
        return categories
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/judges/{commission_id}",
    response_model=List[JudgeResponse],
    summary="Get judges by commission",
    description="Retrieve list of judges for a specific commission"
)
async def get_judges(commission_id: int):
    """Get all judges for a commission."""
    try:
        judges = await mapper_service.get_judges_by_commission(commission_id)
        return judges
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== CASE SEARCH ENDPOINTS ====================

@router.post(
    "/cases/by-case-number",
    response_model=List[CaseResponse],
    summary="Search cases by case number",
    description="Search for cases by case number in District Consumer Courts"
)
async def search_by_case_number(request: CaseSearchRequest = Body(...)):
    """
    Search cases by case number.
    
    - **state**: State name (e.g., "KARNATAKA")
    - **commission**: Commission name (e.g., "Bangalore 1st & Rural Additional")
    - **search_value**: Case number to search for
    - **from_date**: Start date (YYYY-MM-DD) - optional
    - **to_date**: End date (YYYY-MM-DD) - optional
    - **page**: Page number (0-indexed) - optional
    - **size**: Page size (1-100) - optional
    """
    try:
        cases = await case_service.search_by_case_number(request)
        return cases
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/cases/by-complainant",
    response_model=List[CaseResponse],
    summary="Search cases by complainant name",
    description="Search for cases by complainant name in District Consumer Courts"
)
async def search_by_complainant(request: CaseSearchRequest = Body(...)):
    """Search cases by complainant name."""
    try:
        cases = await case_service.search_by_complainant(request)
        return cases
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/cases/by-respondent",
    response_model=List[CaseResponse],
    summary="Search cases by respondent name",
    description="Search for cases by respondent name in District Consumer Courts"
)
async def search_by_respondent(request: CaseSearchRequest = Body(...)):
    """Search cases by respondent name."""
    try:
        cases = await case_service.search_by_respondent(request)
        return cases
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/cases/by-complainant-advocate",
    response_model=List[CaseResponse],
    summary="Search cases by complainant advocate",
    description="Search for cases by complainant advocate name in District Consumer Courts"
)
async def search_by_complainant_advocate(request: CaseSearchRequest = Body(...)):
    """Search cases by complainant advocate name."""
    try:
        cases = await case_service.search_by_complainant_advocate(request)
        return cases
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/cases/by-respondent-advocate",
    response_model=List[CaseResponse],
    summary="Search cases by respondent advocate",
    description="Search for cases by respondent advocate name in District Consumer Courts"
)
async def search_by_respondent_advocate(request: CaseSearchRequest = Body(...)):
    """Search cases by respondent advocate name."""
    try:
        cases = await case_service.search_by_respondent_advocate(request)
        return cases
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/cases/by-industry-type",
    response_model=List[CaseResponse],
    summary="Search cases by industry type",
    description="Search for cases by industry category in District Consumer Courts"
)
async def search_by_industry_type(request: IndustryTypeSearchRequest = Body(...)):
    """
    Search cases by industry type/category.
    
    You can provide either category_name (e.g., "BANKING") or category_id.
    If both are provided, category_id takes precedence.
    """
    try:
        cases = await case_service.search_by_industry_type(request)
        return cases
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/cases/by-judge",
    response_model=List[CaseResponse],
    summary="Search cases by judge",
    description="Search for cases by judge name in District Consumer Courts"
)
async def search_by_judge(request: JudgeSearchRequest = Body(...)):
    """
    Search cases by judge.
    
    You can provide either judge_name or judge_id.
    If both are provided, judge_id takes precedence.
    """
    try:
        cases = await case_service.search_by_judge(request)
        return cases
    except JagritiAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
