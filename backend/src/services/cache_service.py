"""
Cache Service for Redis-based caching functionality
"""

import json
import logging
from typing import Any, Optional, Dict
import redis.asyncio as redis
from datetime import timedelta

from src.config.settings import get_settings
from src.schemas.sql_analysis import SQLAnalysisResult

logger = logging.getLogger(__name__)


class CacheService:
    """
    Service for managing cache operations with Redis backend.
    Handles caching of analysis results, student profiles, and other frequently accessed data.
    """
    
    def __init__(self, redis_client: redis.Redis):
        """Initialize cache service with Redis client"""
        self.redis = redis_client
        self.settings = get_settings()
        
        # Cache key prefixes for different data types
        self.ANALYSIS_PREFIX = "analysis:"
        self.PROFILE_PREFIX = "profile:"
        self.HINTS_PREFIX = "hints:"
        self.CONCEPTS_PREFIX = "concepts:"
        
    async def get_analysis_cache(self, cache_key: str) -> Optional[SQLAnalysisResult]:
        """
        Retrieve cached SQL analysis result
        """
        try:
            full_key = f"{self.ANALYSIS_PREFIX}{cache_key}"
            cached_data = await self.redis.get(full_key)
            
            if cached_data:
                data_dict = json.loads(cached_data)
                logger.debug(f"Cache hit for analysis: {cache_key}")
                return SQLAnalysisResult(**data_dict)
                
            logger.debug(f"Cache miss for analysis: {cache_key}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving analysis cache: {str(e)}")
            return None
    
    async def set_analysis_cache(
        self, 
        cache_key: str, 
        result: SQLAnalysisResult,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache SQL analysis result with optional TTL
        """
        try:
            full_key = f"{self.ANALYSIS_PREFIX}{cache_key}"
            ttl = ttl or self.settings.cache_ttl_analysis
            
            # Convert Pydantic model to JSON
            cache_data = result.model_dump_json()
            
            await self.redis.setex(full_key, ttl, cache_data)
            logger.debug(f"Cached analysis result: {cache_key}, TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Error setting analysis cache: {str(e)}")
            return False
    
    async def get_student_profile_cache(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached student profile data
        """
        try:
            full_key = f"{self.PROFILE_PREFIX}{student_id}"
            cached_data = await self.redis.get(full_key)
            
            if cached_data:
                logger.debug(f"Cache hit for profile: {student_id}")
                return json.loads(cached_data)
                
            logger.debug(f"Cache miss for profile: {student_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving profile cache: {str(e)}")
            return None
    
    async def set_student_profile_cache(
        self, 
        student_id: str, 
        profile_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache student profile data
        """
        try:
            full_key = f"{self.PROFILE_PREFIX}{student_id}"
            ttl = ttl or self.settings.cache_ttl_profile
            
            cache_data = json.dumps(profile_data, default=str)
            await self.redis.setex(full_key, ttl, cache_data)
            logger.debug(f"Cached profile: {student_id}, TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Error setting profile cache: {str(e)}")
            return False
    
    async def get_hint_cache(self, hint_key: str) -> Optional[str]:
        """
        Retrieve cached hint content
        """
        try:
            full_key = f"{self.HINTS_PREFIX}{hint_key}"
            cached_hint = await self.redis.get(full_key)
            
            if cached_hint:
                logger.debug(f"Cache hit for hint: {hint_key}")
                return cached_hint
                
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving hint cache: {str(e)}")
            return None
    
    async def set_hint_cache(
        self, 
        hint_key: str, 
        hint_content: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache hint content
        """
        try:
            full_key = f"{self.HINTS_PREFIX}{hint_key}"
            ttl = ttl or self.settings.cache_ttl_hints
            
            await self.redis.setex(full_key, ttl, hint_content)
            logger.debug(f"Cached hint: {hint_key}, TTL: {ttl}s")
            return True
            
        except Exception as e:
            logger.error(f"Error setting hint cache: {str(e)}")
            return False
    
    async def invalidate_student_cache(self, student_id: str) -> bool:
        """
        Invalidate all cache entries for a specific student
        """
        try:
            # Find all keys for this student
            patterns = [
                f"{self.PROFILE_PREFIX}{student_id}",
                f"{self.ANALYSIS_PREFIX}*{student_id}*",
                f"{self.HINTS_PREFIX}*{student_id}*"
            ]
            
            deleted_count = 0
            for pattern in patterns:
                keys = await self.redis.keys(pattern)
                if keys:
                    deleted_count += await self.redis.delete(*keys)
            
            logger.info(f"Invalidated {deleted_count} cache entries for student: {student_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating student cache: {str(e)}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics and health information
        """
        try:
            info = await self.redis.info()
            
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "Unknown"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0), 
                    info.get("keyspace_misses", 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Error retrieving cache stats: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        return round((hits / total * 100) if total > 0 else 0.0, 2)
    
    async def health_check(self) -> bool:
        """
        Check if Redis connection is healthy
        """
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return False 