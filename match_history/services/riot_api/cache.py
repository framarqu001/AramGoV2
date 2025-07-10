"""
Cache module for the Riot API service.
"""
import hashlib
import json
import logging
from datetime import timedelta

from django.core.cache import cache

from match_history.services.riot_api.exceptions import RiotAPICacheError

logger = logging.getLogger(__name__)


class RiotAPICache:
    """
    Cache handler for Riot API responses.
    
    This class provides methods for caching and retrieving API responses.
    Different types of data have different TTL (Time To Live) values.
    """
    
    # Default TTL values in seconds
    DEFAULT_TTL = 60 * 60  # 1 hour
    
    # TTL values for different types of data
    TTL_MAPPING = {
        'summoner': 60 * 60,  # 1 hour
        'match': 24 * 60 * 60,  # 24 hours
        'match_list': 5 * 60,  # 5 minutes
        'champion': 24 * 60 * 60,  # 24 hours
        'item': 24 * 60 * 60,  # 24 hours
        'rune': 24 * 60 * 60,  # 24 hours
        'spell': 24 * 60 * 60,  # 24 hours
        'profile_icon': 24 * 60 * 60,  # 24 hours
    }
    
    @staticmethod
    def _generate_cache_key(endpoint, params):
        """
        Generate a cache key based on the endpoint and parameters.
        
        Args:
            endpoint (str): The API endpoint.
            params (dict): The parameters for the API request.
            
        Returns:
            str: The cache key.
        """
        # Convert params to a sorted string representation to ensure consistent keys
        params_str = json.dumps(params, sort_keys=True)
        
        # Generate a hash of the endpoint and params
        key = f"riot_api:{endpoint}:{hashlib.md5(params_str.encode()).hexdigest()}"
        
        return key
    
    @classmethod
    def get(cls, endpoint, params):
        """
        Get a cached API response.
        
        Args:
            endpoint (str): The API endpoint.
            params (dict): The parameters for the API request.
            
        Returns:
            dict or None: The cached response, or None if not found.
        """
        cache_key = cls._generate_cache_key(endpoint, params)
        
        try:
            cached_data = cache.get(cache_key)
            
            if cached_data:
                logger.debug(f"Cache hit for {endpoint}")
                return cached_data
            
            logger.debug(f"Cache miss for {endpoint}")
            return None
        except Exception as e:
            logger.error(f"Error getting cached data for {endpoint}: {e}")
            raise RiotAPICacheError(f"Error getting cached data: {e}")
    
    @classmethod
    def set(cls, endpoint, params, data, ttl=None):
        """
        Cache an API response.
        
        Args:
            endpoint (str): The API endpoint.
            params (dict): The parameters for the API request.
            data (dict): The API response to cache.
            ttl (int, optional): Time to live in seconds. Defaults to None.
            
        Returns:
            bool: True if the data was cached successfully, False otherwise.
        """
        cache_key = cls._generate_cache_key(endpoint, params)
        
        # Determine the TTL based on the endpoint type
        if ttl is None:
            # Extract the endpoint type from the endpoint string
            endpoint_type = endpoint.split('/')[0] if '/' in endpoint else endpoint
            ttl = cls.TTL_MAPPING.get(endpoint_type, cls.DEFAULT_TTL)
        
        try:
            cache.set(cache_key, data, timeout=ttl)
            logger.debug(f"Cached data for {endpoint} with TTL {ttl}")
            return True
        except Exception as e:
            logger.error(f"Error caching data for {endpoint}: {e}")
            raise RiotAPICacheError(f"Error caching data: {e}")
    
    @classmethod
    def delete(cls, endpoint, params):
        """
        Delete a cached API response.
        
        Args:
            endpoint (str): The API endpoint.
            params (dict): The parameters for the API request.
            
        Returns:
            bool: True if the data was deleted successfully, False otherwise.
        """
        cache_key = cls._generate_cache_key(endpoint, params)
        
        try:
            cache.delete(cache_key)
            logger.debug(f"Deleted cached data for {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cached data for {endpoint}: {e}")
            raise RiotAPICacheError(f"Error deleting cached data: {e}")