import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional, Dict, Any
import logging
import time
from app.config import get_settings
from app.utils.exceptions import APITimeoutException, APIConnectionException, JagritiAPIException


class JagritiClient:
    """HTTP client for Jagriti API with retry logic"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.JAGRITI_BASE_URL
        self.timeout = self.settings.REQUEST_TIMEOUT
        self.logger = logging.getLogger("app.jagriti_client")
        
        # Common headers for all requests
        self.headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        self.logger.info(f"🌐 Jagriti client initialized - Base URL: {self.base_url}, Timeout: {self.timeout}s")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        # Log request details
        if params:
            self.logger.info(f"🌐 API CALL: {method} {endpoint} - Params: {params}")
        elif json_data:
            # Log all data including serchTypeValue
            self.logger.info(f"🌐 API CALL: {method} {endpoint} - Data: {json_data}")
        else:
            self.logger.info(f"🌐 API CALL: {method} {endpoint}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, params=params, headers=self.headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=json_data, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                result = response.json()
                
                # Log successful response
                elapsed = time.time() - start_time
                data_count = len(result.get('data', [])) if isinstance(result.get('data'), list) else 'N/A'
                self.logger.info(f"✅ API SUCCESS: {method} {endpoint} - Status: {response.status_code} - Time: {elapsed:.3f}s - Items: {data_count}")
                
                return result
                
        except httpx.TimeoutException:
            elapsed = time.time() - start_time
            self.logger.error(f"⏰ API TIMEOUT: {method} {endpoint} - Time: {elapsed:.3f}s")
            raise APITimeoutException()
        except httpx.ConnectError:
            elapsed = time.time() - start_time
            self.logger.error(f"🔌 API CONNECTION ERROR: {method} {endpoint} - Time: {elapsed:.3f}s")
            raise APIConnectionException()
        except httpx.HTTPStatusError as e:
            elapsed = time.time() - start_time
            self.logger.error(f"🚨 API HTTP ERROR: {method} {endpoint} - Status: {e.response.status_code} - Time: {elapsed:.3f}s")
            raise JagritiAPIException(
                message=f"API returned error: {e.response.status_code}",
                status_code=e.response.status_code
            )
        except Exception as e:
            elapsed = time.time() - start_time
            self.logger.error(f"💥 API UNEXPECTED ERROR: {method} {endpoint} - Error: {str(e)} - Time: {elapsed:.3f}s")
            raise JagritiAPIException(
                message=f"Unexpected error: {str(e)}",
                status_code=500
            )
    
    async def get_states(self) -> Dict[str, Any]:
        """Get all states and commissions"""
        return await self._make_request(
            method="GET",
            endpoint="/services/report/report/getStateCommissionAndCircuitBench"
        )
    
    async def get_districts(self, commission_id: int) -> Dict[str, Any]:
        """Get districts by commission ID"""
        return await self._make_request(
            method="GET",
            endpoint="/services/report/report/getDistrictCommissionByCommissionId",
            params={"commissionId": commission_id}
        )
    
    async def get_categories(self) -> Dict[str, Any]:
        """Get all case categories"""
        return await self._make_request(
            method="POST",
            endpoint="/services/master/master/v2/caseCategory",
            json_data={"caseCategoryLevel": 1, "parentCaseCategoryId": 0}
        )
    
    async def get_judges(self, commission_id: int) -> Dict[str, Any]:
        """Get judges by commission ID"""
        return await self._make_request(
            method="GET",
            endpoint="/services/master/master/v2/getJudgeListForHearing",
            params={"commissionId": commission_id, "activeStatus": True}
        )
    
    async def search_cases(
        self,
        commission_id: int,
        search_type: int,
        search_value: str,
        from_date: str,
        to_date: str,
        page: int = 0,
        size: int = 30,
        judge_id: str = ""
    ) -> Dict[str, Any]:
        """
        Search cases by various criteria
        
        Args:
            commission_id: Commission or district ID
            search_type: 1-7 (case number, complainant, respondent, etc.)
            search_value: Search value or ID
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            page: Page number
            size: Page size
            judge_id: Judge ID (only for judge search)
        """
        # For industry (6) and judge (7), use dateRequestType=2, others use 1
        date_request_type = 2 if search_type in [6, 7] else 1
        
        payload = {
            "commissionId": commission_id,
            "page": page,
            "size": size,
            "fromDate": from_date,
            "toDate": to_date,
            "dateRequestType": date_request_type,
            "serchType": search_type,
            "serchTypeValue": search_value,
            "judgeId": judge_id
        }
        
        return await self._make_request(
            method="POST",
            endpoint="/services/case/caseFilingService/v2/getCaseDetailsBySearchType",
            json_data=payload
        )


jagriti_client = JagritiClient()