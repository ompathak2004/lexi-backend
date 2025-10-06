from typing import Optional, Any
from datetime import datetime, timedelta
import hashlib
import json
import logging
from cachetools import TTLCache


class CacheService:
    """Smart in-memory cache with TTL support"""
    
    def __init__(self):
        self.logger = logging.getLogger("app.cache")
        
        # Static data caches (simple variables with timestamps)
        self.states_cache: Optional[Any] = None
        self.states_cache_time: Optional[datetime] = None
        
        self.categories_cache: Optional[Any] = None
        self.categories_cache_time: Optional[datetime] = None
        
        # Dynamic data with TTL and LRU eviction (slot-based)
        self.commissions_cache = TTLCache(maxsize=50, ttl=21600)  # 6 hours
        self.judges_cache = TTLCache(maxsize=100, ttl=21600)  # 6 hours
        self.cases_cache = TTLCache(maxsize=200, ttl=300)  # 5 minutes
        
        self.logger.info("🗄️ Cache service initialized - States: Manual TTL, Commissions: 6h, Judges: 6h, Cases: 5min")
    
    def _is_cache_valid(self, cache_time: Optional[datetime], ttl_seconds: int) -> bool:
        """Check if cache is still valid based on TTL"""
        if cache_time is None:
            return False
        return datetime.now() - cache_time < timedelta(seconds=ttl_seconds)
    
    def _generate_cache_key(self, **kwargs) -> str:
        """Generate unique cache key from parameters"""
        key_string = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    # ==================== STATES CACHE ====================
    
    def get_states(self) -> Optional[Any]:
        """Get cached states list"""
        if self.states_cache is not None:
            self.logger.debug("🎯 CACHE HIT: States data retrieved from cache")
            return self.states_cache
        self.logger.debug("❌ CACHE MISS: States data not in cache")
        return None
    
    def set_states(self, data: Any):
        """Set states cache"""
        self.states_cache = data
        self.states_cache_time = datetime.now()
        self.logger.info(f"💾 CACHE SET: States data cached ({len(data) if isinstance(data, list) else 'N/A'} items)")
    
    def is_states_valid(self, ttl: int) -> bool:
        """Check if states cache is valid"""
        is_valid = self._is_cache_valid(self.states_cache_time, ttl)
        if is_valid:
            self.logger.debug(f"✅ States cache is VALID (TTL: {ttl}s)")
        else:
            self.logger.debug(f"⏰ States cache is EXPIRED (TTL: {ttl}s)")
        return is_valid
    
    # ==================== CATEGORIES CACHE ====================
    
    def get_categories(self) -> Optional[Any]:
        """Get cached categories list"""
        if self.categories_cache is not None:
            self.logger.debug("🎯 CACHE HIT: Categories data retrieved from cache")
            return self.categories_cache
        self.logger.debug("❌ CACHE MISS: Categories data not in cache")
        return None
    
    def set_categories(self, data: Any):
        """Set categories cache"""
        self.categories_cache = data
        self.categories_cache_time = datetime.now()
        self.logger.info(f"💾 CACHE SET: Categories data cached ({len(data) if isinstance(data, list) else 'N/A'} items)")
    
    def is_categories_valid(self, ttl: int) -> bool:
        """Check if categories cache is valid"""
        return self._is_cache_valid(self.categories_cache_time, ttl)
    
    # ==================== COMMISSIONS CACHE ====================
    
    def get_commissions(self, state_id: int) -> Optional[Any]:
        """Get cached commissions for a state"""
        key = f"commissions_{state_id}"
        data = self.commissions_cache.get(key)
        if data is not None:
            self.logger.debug(f"🎯 CACHE HIT: Commissions for state {state_id} retrieved from cache")
            return data
        self.logger.debug(f"❌ CACHE MISS: Commissions for state {state_id} not in cache")
        return None
    
    def set_commissions(self, state_id: int, data: Any):
        """Set commissions cache for a state"""
        key = f"commissions_{state_id}"
        self.commissions_cache[key] = data
        self.logger.info(f"💾 CACHE SET: Commissions for state {state_id} cached ({len(data) if isinstance(data, list) else 'N/A'} items)")
    
    # ==================== JUDGES CACHE ====================
    
    def get_judges(self, commission_id: int) -> Optional[Any]:
        """Get cached judges for a commission"""
        key = f"judges_{commission_id}"
        data = self.judges_cache.get(key)
        if data is not None:
            self.logger.debug(f"🎯 CACHE HIT: Judges for commission {commission_id} retrieved from cache")
            return data
        self.logger.debug(f"❌ CACHE MISS: Judges for commission {commission_id} not in cache")
        return None
    
    def set_judges(self, commission_id: int, data: Any):
        """Set judges cache for a commission"""
        key = f"judges_{commission_id}"
        self.judges_cache[key] = data
        self.logger.info(f"💾 CACHE SET: Judges for commission {commission_id} cached ({len(data) if isinstance(data, list) else 'N/A'} items)")
    
    # ==================== CASE RESULTS CACHE ====================
    
    def get_cases(self, **params) -> Optional[Any]:
        """Get cached case search results"""
        key = self._generate_cache_key(**params)
        data = self.cases_cache.get(key)
        if data is not None:
            self.logger.debug(f"🎯 CACHE HIT: Case search results retrieved from cache (key: {key[:12]}...)")
            return data
        self.logger.debug(f"❌ CACHE MISS: Case search results not in cache (key: {key[:12]}...)")
        return None
    
    def set_cases(self, data: Any, **params):
        """Set case search results cache"""
        key = self._generate_cache_key(**params)
        self.cases_cache[key] = data
        self.logger.info(f"💾 CACHE SET: Case search results cached ({len(data) if isinstance(data, list) else 'N/A'} items, key: {key[:12]}...)")
    
    # ==================== CACHE MANAGEMENT ====================
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "states_cached": self.states_cache is not None,
            "categories_cached": self.categories_cache is not None,
            "commissions_count": len(self.commissions_cache),
            "judges_count": len(self.judges_cache),
            "cases_count": len(self.cases_cache),
        }
    
    def clear_all(self):
        """Clear all caches"""
        self.logger.warning("🧹 CACHE CLEAR: Clearing all cached data")
        self.states_cache = None
        self.states_cache_time = None
        self.categories_cache = None
        self.categories_cache_time = None
        self.commissions_cache.clear()
        self.judges_cache.clear()
        self.cases_cache.clear()
        self.logger.info("✅ All caches cleared successfully")


cache = CacheService()