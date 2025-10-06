from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from app.services.jagriti_client import jagriti_client
from app.services.mapper_service import mapper_service
from app.services.cache_service import cache
from app.models.requests import CaseSearchRequest, IndustryTypeSearchRequest, JudgeSearchRequest
from app.models.responses import CaseResponse
from app.utils.exceptions import JagritiAPIException, CaseDataException
from app.config import get_settings


class CaseService:
    """Service to handle case search operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger("app.case_service")
    
    def _format_case_data(self, raw_case: Dict[str, Any]) -> CaseResponse:
        """Format raw case data from Jagriti API to our response model"""
        try:
            return CaseResponse(
                case_number=raw_case.get("caseNumber", ""),
                case_stage=raw_case.get("caseStageName", ""),
                filing_date=raw_case.get("caseFilingDate", ""),
                complainant=raw_case.get("complainantName", ""),
                complainant_advocate=raw_case.get("complainantAdvocateName"),
                respondent=raw_case.get("respondentName"),
                respondent_advocate=raw_case.get("respondentAdvocateName"),
                document_link=raw_case.get("documentBase64")  # base64 encoded
            )
        except Exception as e:
            raise CaseDataException(f"Error formatting case data: {str(e)}")
    
    def _get_default_date_range(self) -> tuple[str, str]:
        """Get default date range (current year)"""
        current_year = datetime.now().year
        from_date = f"{current_year}-01-01"
        to_date = f"{current_year}-12-31"
        return from_date, to_date
    
    async def _search_cases_by_type(
        self,
        state_name: str,
        commission_name: str,
        search_value: str,
        search_type: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: int = 0,
        size: int = 30,
        judge_id: str = ""
    ) -> List[CaseResponse]:
        """
        Generic method to search cases by different types.
        
        COMPLETE FLOW:
        1. User calls endpoint (e.g., /by-case-number) with state and commission name
        2. Resolve state name to state ID:
           - Check cache for states (TTL check)
           - If cache miss/expired, call Jagriti API
           - Fuzzy match user's state input to find state ID
        3. Find the specific commission ID:
           - Check cache for commissions linked to this state ID
           - If cache miss, call Jagriti API
           - Fuzzy match user's commission input (e.g., "Mumbai Suburban" matches "Mumbai (Suburban)")
           - Return ONLY the matched commission ID
        4. Call Jagriti API ONCE with the specific commission ID and search_value
        5. Format and return results to user
        
        Args:
            state_name: State name entered by user
            commission_name: Commission name entered by user
            search_value: The search value (case number, name, etc.)
            search_type: Type of search (1-7)
            from_date: Start date for search
            to_date: End date for search
            page: Page number for pagination
            size: Page size
            judge_id: Judge ID (for judge search)
        
        Returns:
            List of formatted case responses
        """
        
        search_type_names = {
            1: "Case Number", 2: "Complainant", 3: "Respondent", 
            4: "Complainant Advocate", 5: "Respondent Advocate", 
            6: "Industry Type", 7: "Judge"
        }
        search_type_name = search_type_names.get(search_type, f"Type {search_type}")
        
        self.logger.info(f"🔍 CASE SEARCH STARTED: {search_type_name} = '{search_value}' in {state_name}/{commission_name}")
        
        # STEP 1, 2 & 3: Resolve state and commission names to specific commission ID
        commission_id = await mapper_service.find_commission_by_name(
            state_name, commission_name
        )
        
        self.logger.info(f"🎯 Commission resolved: '{commission_name}' -> ID {commission_id}")
        
        # Use default date range if not provided
        if not from_date or not to_date:
            from_date, to_date = self._get_default_date_range()
            self.logger.debug(f"📅 Using default date range: {from_date} to {to_date}")
        else:
            self.logger.debug(f"📅 Using provided date range: {from_date} to {to_date}")
        
        # STEP 4: Call Jagriti API ONCE with the specific commission ID
        self.logger.info(f"🔍 Calling Jagriti API for commission {commission_id}")
        
        response = await jagriti_client.search_cases(
            commission_id=commission_id,
            search_type=search_type,
            search_value=search_value,
            from_date=from_date,
            to_date=to_date,
            page=page,
            size=size,
            judge_id=judge_id
        )
        
        # Extract cases from response
        data = response.get("data", [])
        cases_data = data if isinstance(data, list) else data.get("content", [])
        
        self.logger.info(f"📋 Found {len(cases_data)} cases from commission {commission_id}")
        
        # STEP 5: Format each case and add to results
        all_cases = []
        formatted_count = 0
        for raw_case in cases_data:
            try:
                formatted_case = self._format_case_data(raw_case)
                all_cases.append(formatted_case)
                formatted_count += 1
            except Exception as e:
                # Log error but continue processing other cases
                self.logger.warning(f"⚠️ Error formatting case: {e}")
                continue
        
        self.logger.info(f"🎉 SEARCH COMPLETE: Successfully formatted {formatted_count}/{len(cases_data)} cases")
        return all_cases
    
    async def search_by_case_number(self, request: CaseSearchRequest) -> List[CaseResponse]:
        """Search cases by case number (search_type = 1)"""
        return await self._search_cases_by_type(
            state_name=request.state,
            commission_name=request.commission,
            search_value=request.search_value,
            search_type=1,
            from_date=request.from_date,
            to_date=request.to_date,
            page=request.page,
            size=request.size
        )
    
    async def search_by_complainant(self, request: CaseSearchRequest) -> List[CaseResponse]:
        """Search cases by complainant name (search_type = 2)"""
        return await self._search_cases_by_type(
            state_name=request.state,
            commission_name=request.commission,
            search_value=request.search_value,
            search_type=2,
            from_date=request.from_date,
            to_date=request.to_date,
            page=request.page,
            size=request.size
        )
    
    async def search_by_respondent(self, request: CaseSearchRequest) -> List[CaseResponse]:
        """Search cases by respondent name (search_type = 3)"""
        return await self._search_cases_by_type(
            state_name=request.state,
            commission_name=request.commission,
            search_value=request.search_value,
            search_type=3,
            from_date=request.from_date,
            to_date=request.to_date,
            page=request.page,
            size=request.size
        )
    
    async def search_by_complainant_advocate(self, request: CaseSearchRequest) -> List[CaseResponse]:
        """Search cases by complainant advocate (search_type = 4)"""
        return await self._search_cases_by_type(
            state_name=request.state,
            commission_name=request.commission,
            search_value=request.search_value,
            search_type=4,
            from_date=request.from_date,
            to_date=request.to_date,
            page=request.page,
            size=request.size
        )
    
    async def search_by_respondent_advocate(self, request: CaseSearchRequest) -> List[CaseResponse]:
        """Search cases by respondent advocate (search_type = 5)"""
        return await self._search_cases_by_type(
            state_name=request.state,
            commission_name=request.commission,
            search_value=request.search_value,
            search_type=5,
            from_date=request.from_date,
            to_date=request.to_date,
            page=request.page,
            size=request.size
        )
    
    async def search_by_industry_type(self, request: IndustryTypeSearchRequest) -> List[CaseResponse]:
        """Search cases by industry type/category (search_type = 6)"""
        # Resolve category name to ID if needed
        search_value = request.category_id or request.category_name
        if request.category_name and not request.category_id:
            category = await mapper_service.find_category_by_name(request.category_name)
            search_value = str(category["category_id"])
        
        return await self._search_cases_by_type(
            state_name=request.state,
            commission_name=request.commission,
            search_value=str(search_value),
            search_type=6,
            from_date=request.from_date,
            to_date=request.to_date,
            page=request.page,
            size=request.size
        )
    
    async def search_by_judge(self, request: JudgeSearchRequest) -> List[CaseResponse]:
        """Search cases by judge (search_type = 7)"""
        # Resolve judge name to ID if needed
        judge_id = request.judge_id
        if request.judge_name and not request.judge_id:
            # First get the commission ID to search judges
            commission_id = await mapper_service.find_commission_by_name(
                request.state, request.commission
            )
            
            judge = await mapper_service.find_judge_by_name(
                commission_id, request.judge_name
            )
            judge_id = judge["judge_id"]
        
        return await self._search_cases_by_type(
            state_name=request.state,
            commission_name=request.commission,
            search_value="",  # Empty for judge search
            search_type=7,
            from_date=request.from_date,
            to_date=request.to_date,
            page=request.page,
            size=request.size,
            judge_id=str(judge_id)
        )


case_service = CaseService()