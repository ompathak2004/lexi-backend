from typing import Optional, List, Dict, Any, Tuple
import logging
import asyncio
from app.services.jagriti_client import jagriti_client
from app.services.cache_service import cache
from app.config import get_settings
from app.utils.exceptions import (
    StateNotFoundException,
    CommissionNotFoundException,
    CategoryNotFoundException,
    JudgeNotFoundException
)


class MapperService:
    """Service to map text inputs to Jagriti API IDs"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger("app.mapper")
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison - removes spaces, parentheses, and converts to uppercase"""
        normalized = text.strip().upper()
        normalized = normalized.replace("(", "").replace(")", "").replace(" ", "")
        return normalized
    
    def _fuzzy_match(self, search_text: str, target_text: str) -> bool:
        """Check if texts match (case-insensitive, flexible, ignores parentheses and spaces)"""
        search = self._normalize_text(search_text)
        target = self._normalize_text(target_text)
        
        if search == target:
            return True
        
        if search in target:
            return True
        
        return False
    
    async def get_all_states(self) -> List[Dict[str, Any]]:
        """Get all states with caching"""
        self.logger.debug("🗺️ Requesting all states...")
        
        # Check cache first (cache stores formatted data)
        if cache.is_states_valid(self.settings.CACHE_TTL_STATES):
            cached_data = cache.get_states()
            if cached_data:
                self.logger.debug(f"📋 Returning {len(cached_data)} states from cache")
                return cached_data
        
        # Cache miss/expired - Fetch from API
        self.logger.info("🌐 Cache miss/expired - Fetching states from Jagriti API")
        response = await jagriti_client.get_states()
        states_data = response.get("data", [])
        
        # Filter only District Consumer Courts (DCDRC)
        filtered_states = [
            {
                "commission_id": s["commissionId"],
                "commission_name": s["commissionNameEn"],
                "is_circuit_bench": s["circuitAdditionBenchStatus"],
                "is_active": s["activeStatus"]
            }
            for s in states_data
            # if s["activeStatus"] and not s["circuitAdditionBenchStatus"]
            if s["activeStatus"] 
        ]
        
        self.logger.info(f"📋 Filtered {len(filtered_states)} active DCDRC states from {len(states_data)} total")
        
        # Cache the formatted result
        cache.set_states(filtered_states)
        
        return filtered_states
    
    async def find_state_by_name(self, state_name: str) -> Dict[str, Any]:
        """Find state by name"""
        self.logger.debug(f"🔍 Searching for state: '{state_name}'")
        states = await self.get_all_states()
        
        for state in states:
            if self._fuzzy_match(state_name, state["commission_name"]):
                self.logger.info(f"✅ State found: '{state_name}' -> ID {state['commission_id']} ({state['commission_name']})")
                return state
        
        self.logger.error(f"❌ State not found: '{state_name}'")
        raise StateNotFoundException(state_name)
    
    async def get_commissions_by_state(self, state_id: int) -> List[Dict[str, Any]]:
        """Get all commissions/districts for a state with caching"""
        self.logger.debug(f"🏛️ Requesting commissions for state {state_id}...")
        
        # Check cache first (cache stores formatted data)
        cached_data = cache.get_commissions(state_id)
        if cached_data is not None:
            self.logger.debug(f"📋 Returning {len(cached_data)} commissions from cache for state {state_id}")
            return cached_data
        
        # Cache miss - Fetch from API
        self.logger.info(f"🌐 Cache miss - Fetching commissions for state {state_id} from Jagriti API")
        response = await jagriti_client.get_districts(state_id)
        districts_data = response.get("data", [])
        
        # Format the districts data
        formatted_districts = [
            {
                "commission_id": d["commissionId"],
                "commission_name": d["commissionNameEn"],
                "is_circuit_bench": d["circuitAdditionBenchStatus"],
                "is_active": d["activeStatus"]
            }
            for d in districts_data
            if d["activeStatus"]
        ]
        
        self.logger.info(f"📋 Formatted {len(formatted_districts)} active commissions for state {state_id}")
        
        # Cache the formatted result
        cache.set_commissions(state_id, formatted_districts)
        
        return formatted_districts
    
    async def find_commission_by_name(
        self, 
        state_name: str, 
        commission_name: str
    ) -> int:
        """
        Find commission by name and return the specific commission ID.
        
        FLOW:
        1. Find state ID by name (uses cache if available, else calls API)
        2. Get all commissions for that state (uses cache if available, else calls API)
        3. Fuzzy match the commission name entered by user (ignores spaces, parentheses)
        4. Prioritize non-circuit benches over circuit benches (e.g., "Mumbai(Suburban)" over "Additional DCF, Mumbai(Suburban)")
        5. If match found, return that specific commission ID
        6. If no match, raise CommissionNotFoundException
        
        Args:
            state_name: State name entered by user (e.g., "Maharashtra")
            commission_name: Commission name entered by user (e.g., "Mumbai Suburban" or "Mumbai(Suburban)")
        
        Returns:
            commission_id: The specific commission ID that matches the user's input
        
        Raises:
            CommissionNotFoundException: If the commission name doesn't match any commission
        """
        self.logger.debug(f"🔍 Searching for commission: '{commission_name}' in state '{state_name}'")
        
        # STEP 1: Find the state ID (cache-first)
        state = await self.find_state_by_name(state_name)
        state_id = state["commission_id"]
        self.logger.info(f"✅ State resolved: '{state_name}' -> ID {state_id}")
        
        # STEP 2: Get all commissions/districts for this state (cache-first)
        commissions = await self.get_commissions_by_state(state_id)
        
        # STEP 3: If no districts exist, the state itself is the commission
        if not commissions:
            self.logger.info(f"📍 No districts found for state {state_id} - returning state level commission")
            return state_id
        
        # STEP 4: Find all matching commissions with fuzzy matching
        # Collect all matches and prioritize non-circuit benches
        matches = []
        for commission in commissions:
            if self._fuzzy_match(commission_name, commission["commission_name"]):
                is_circuit = commission.get("is_circuit_bench", False)
                matches.append({
                    "commission": commission,
                    "is_circuit": is_circuit
                })
                self.logger.debug(f"📍 Match found: '{commission['commission_name']}' (ID: {commission['commission_id']}, Circuit: {is_circuit})")
        
        # STEP 5: If matches found, prioritize non-circuit benches
        if matches:
            # Sort by circuit status (False first, meaning non-circuit benches first)
            matches.sort(key=lambda x: x["is_circuit"])
            
            selected = matches[0]["commission"]
            self.logger.info(f"✅ Commission matched: '{commission_name}' -> '{selected['commission_name']}' (ID: {selected['commission_id']})")
            
            # Log if we had multiple matches and chose the non-circuit one
            if len(matches) > 1:
                self.logger.info(f"📌 Multiple matches found ({len(matches)}), prioritized non-circuit bench: '{selected['commission_name']}'")
            
            return selected["commission_id"]
        
        # STEP 6: If no match found, raise exception
        available_commissions = [c["commission_name"] for c in commissions]
        self.logger.error(f"❌ Commission not found: '{commission_name}' in state '{state_name}'")
        raise CommissionNotFoundException(
            f"Commission '{commission_name}' not found in state '{state_name}'. "
            f"Available commissions: {', '.join(available_commissions)}"
        )
    
    async def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all case categories with caching"""
        self.logger.debug("📚 Requesting all categories...")
        
        # Check cache first (cache stores formatted data)
        if cache.is_categories_valid(self.settings.CACHE_TTL_CATEGORIES):
            cached_data = cache.get_categories()
            if cached_data:
                self.logger.debug(f"📋 Returning {len(cached_data)} categories from cache")
                return cached_data
        
        # Cache miss/expired - Fetch from API
        self.logger.info("🌐 Cache miss/expired - Fetching categories from Jagriti API")
        response = await jagriti_client.get_categories()
        categories_data = response.get("data", [])
        
        # Format the categories data
        formatted_categories = [
            {
                "category_id": c["caseCategoryId"],
                "category_name": c["caseCategoryNameEn"]
            }
            for c in categories_data
        ]
        
        self.logger.info(f"📋 Formatted {len(formatted_categories)} categories")
        
        # Cache the formatted result
        cache.set_categories(formatted_categories)
        
        return formatted_categories
    
    async def find_category_by_name(self, category_name: str) -> Dict[str, Any]:
        """Find category by name"""
        categories = await self.get_all_categories()
        
        for category in categories:
            if self._fuzzy_match(category_name, category["category_name"]):
                return category
        
        raise CategoryNotFoundException(category_name)
    
    async def get_judges_by_commission(self, commission_id: int) -> List[Dict[str, Any]]:
        """Get all judges for a commission with caching"""
        self.logger.debug(f"👨‍⚖️ Requesting judges for commission {commission_id}...")
        
        # Check cache first (cache stores formatted data)
        cached_data = cache.get_judges(commission_id)
        if cached_data is not None:
            self.logger.debug(f"📋 Returning {len(cached_data)} judges from cache for commission {commission_id}")
            return cached_data
        
        # Cache miss - Fetch from API
        self.logger.info(f"🌐 Cache miss - Fetching judges for commission {commission_id} from Jagriti API")
        response = await jagriti_client.get_judges(commission_id)
        judges_data = response.get("data", [])
        
        # Format the judges data
        formatted_judges = [
            {
                "judge_id": j["judgeId"],
                "judge_name": j["judgeName"],
                "commission_id": commission_id
            }
            for j in judges_data
        ]
        
        self.logger.info(f"📋 Formatted {len(formatted_judges)} judges for commission {commission_id}")
        
        # Cache the formatted result
        cache.set_judges(commission_id, formatted_judges)
        
        return formatted_judges
    
    async def find_judge_by_name(self, commission_id: int, judge_name: str) -> Dict[str, Any]:
        """Find judge by name in a specific commission"""
        judges = await self.get_judges_by_commission(commission_id)
        
        for judge in judges:
            if self._fuzzy_match(judge_name, judge["judge_name"]):
                return judge
        
        raise JudgeNotFoundException(judge_name)


mapper_service = MapperService()