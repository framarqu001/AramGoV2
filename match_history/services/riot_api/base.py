"""
Base client for the Riot API service.
"""
import logging
import time
from typing import Dict, Any, Optional, Union

import requests
from django.conf import settings
from riotwatcher import LolWatcher, ApiError

from match_history.services.riot_api.cache import RiotAPICache
from match_history.services.riot_api.exceptions import (
    RiotAPIError,
    RiotAPIRateLimitError,
    RiotAPINotFoundError,
    RiotAPIForbiddenError,
    RiotAPIServerError,
    RiotAPITimeoutError,
    RiotAPIServiceUnavailableError,
)

logger = logging.getLogger(__name__)


class RiotAPIClient:
    """
    Base client for interacting with the Riot Games API.
    
    This class provides methods for making authenticated requests to the Riot API,
    handling rate limiting, errors, and caching responses.
    """
    
    # Rate limiting parameters
    # These values are based on the Riot API rate limits
    # See: https://developer.riotgames.com/rate-limiting.html
    DEFAULT_RETRY_ATTEMPTS = 3
    DEFAULT_RETRY_DELAY = 1  # seconds
    
    # API response codes
    HTTP_TOO_MANY_REQUESTS = 429
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_SERVER_ERROR = 500
    HTTP_SERVICE_UNAVAILABLE = 503
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        region: str = "na1",
        platform: str = "americas",
        use_cache: bool = True,
        retry_attempts: int = DEFAULT_RETRY_ATTEMPTS,
        retry_delay: int = DEFAULT_RETRY_DELAY,
    ):
        """
        Initialize the Riot API client.
        
        Args:
            api_key (str, optional): The Riot API key. Defaults to settings.RIOT_API_KEY.
            region (str, optional): The region to use for API requests. Defaults to "na1".
            platform (str, optional): The platform to use for API requests. Defaults to "americas".
            use_cache (bool, optional): Whether to use caching. Defaults to True.
            retry_attempts (int, optional): Number of retry attempts for rate-limited requests.
                Defaults to DEFAULT_RETRY_ATTEMPTS.
            retry_delay (int, optional): Delay between retry attempts in seconds.
                Defaults to DEFAULT_RETRY_DELAY.
        """
        self.api_key = api_key or settings.RIOT_API_KEY
        self.region = region
        self.platform = platform
        self.use_cache = use_cache
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Initialize the RiotWatcher client
        self.lol_watcher = LolWatcher(self.api_key)
        
        # Base URLs for different API endpoints
        self.base_urls = {
            "region": f"https://{region}.api.riotgames.com",
            "platform": f"https://{platform}.api.riotgames.com",
        }
        
        logger.debug(f"Initialized RiotAPIClient for region {region} and platform {platform}")
    
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        base_url_type: str = "region",
        method: str = "GET",
        use_cache: bool = None,
        ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to the Riot API.
        
        Args:
            endpoint (str): The API endpoint to request.
            params (Dict[str, Any], optional): Query parameters for the request. Defaults to None.
            base_url_type (str, optional): The type of base URL to use. Defaults to "region".
            method (str, optional): The HTTP method to use. Defaults to "GET".
            use_cache (bool, optional): Whether to use caching for this request.
                Defaults to the instance's use_cache value.
            ttl (int, optional): Time to live for the cached response in seconds.
                Defaults to None (use default TTL).
                
        Returns:
            Dict[str, Any]: The API response.
            
        Raises:
            RiotAPIRateLimitError: If the rate limit is exceeded.
            RiotAPINotFoundError: If the resource is not found.
            RiotAPIForbiddenError: If the API key is invalid or has insufficient permissions.
            RiotAPIServerError: If the Riot API server returns an error.
            RiotAPITimeoutError: If the request times out.
            RiotAPIServiceUnavailableError: If the Riot API service is unavailable.
            RiotAPIError: For other API errors.
        """
        params = params or {}
        use_cache = self.use_cache if use_cache is None else use_cache
        
        # Check cache first if caching is enabled
        if use_cache:
            cached_response = RiotAPICache.get(endpoint, params)
            if cached_response:
                return cached_response
        
        # Prepare the request
        url = f"{self.base_urls[base_url_type]}/{endpoint}"
        headers = {"X-Riot-Token": self.api_key}
        
        # Make the request with retry logic for rate limiting
        attempts = 0
        while attempts <= self.retry_attempts:
            try:
                logger.debug(f"Making {method} request to {url} with params {params}")
                response = requests.request(method, url, headers=headers, params=params, timeout=10)
                
                # Handle different response status codes
                if response.status_code == 200:
                    data = response.json()
                    
                    # Cache the response if caching is enabled
                    if use_cache:
                        RiotAPICache.set(endpoint, params, data, ttl)
                    
                    return data
                
                elif response.status_code == self.HTTP_TOO_MANY_REQUESTS:
                    # Handle rate limiting
                    retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                    logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                    
                    if attempts < self.retry_attempts:
                        time.sleep(retry_after)
                        attempts += 1
                        continue
                    else:
                        raise RiotAPIRateLimitError(
                            f"Rate limit exceeded after {attempts} attempts",
                            status_code=response.status_code,
                            response=response.text,
                        )
                
                elif response.status_code == self.HTTP_NOT_FOUND:
                    raise RiotAPINotFoundError(
                        f"Resource not found: {endpoint}",
                        status_code=response.status_code,
                        response=response.text,
                    )
                
                elif response.status_code == self.HTTP_FORBIDDEN:
                    raise RiotAPIForbiddenError(
                        "Invalid API key or insufficient permissions",
                        status_code=response.status_code,
                        response=response.text,
                    )
                
                elif response.status_code == self.HTTP_SERVER_ERROR:
                    raise RiotAPIServerError(
                        "Riot API server error",
                        status_code=response.status_code,
                        response=response.text,
                    )
                
                elif response.status_code == self.HTTP_SERVICE_UNAVAILABLE:
                    raise RiotAPIServiceUnavailableError(
                        "Riot API service unavailable",
                        status_code=response.status_code,
                        response=response.text,
                    )
                
                else:
                    raise RiotAPIError(
                        f"Unexpected API error: {response.status_code}",
                        status_code=response.status_code,
                        response=response.text,
                    )
            
            except requests.exceptions.Timeout:
                raise RiotAPITimeoutError("Request timed out")
            
            except requests.exceptions.RequestException as e:
                raise RiotAPIError(f"Request error: {e}")
            
            except Exception as e:
                raise RiotAPIError(f"Unexpected error: {e}")
    
    def _handle_api_error(self, error: ApiError) -> None:
        """
        Handle errors from the RiotWatcher library.
        
        Args:
            error (ApiError): The API error.
            
        Raises:
            RiotAPIRateLimitError: If the rate limit is exceeded.
            RiotAPINotFoundError: If the resource is not found.
            RiotAPIForbiddenError: If the API key is invalid or has insufficient permissions.
            RiotAPIServerError: If the Riot API server returns an error.
            RiotAPIServiceUnavailableError: If the Riot API service is unavailable.
            RiotAPIError: For other API errors.
        """
        if error.response.status_code == self.HTTP_TOO_MANY_REQUESTS:
            raise RiotAPIRateLimitError(
                "Rate limit exceeded",
                status_code=error.response.status_code,
                response=error.response.text,
            )
        
        elif error.response.status_code == self.HTTP_NOT_FOUND:
            raise RiotAPINotFoundError(
                "Resource not found",
                status_code=error.response.status_code,
                response=error.response.text,
            )
        
        elif error.response.status_code == self.HTTP_FORBIDDEN:
            raise RiotAPIForbiddenError(
                "Invalid API key or insufficient permissions",
                status_code=error.response.status_code,
                response=error.response.text,
            )
        
        elif error.response.status_code == self.HTTP_SERVER_ERROR:
            raise RiotAPIServerError(
                "Riot API server error",
                status_code=error.response.status_code,
                response=error.response.text,
            )
        
        elif error.response.status_code == self.HTTP_SERVICE_UNAVAILABLE:
            raise RiotAPIServiceUnavailableError(
                "Riot API service unavailable",
                status_code=error.response.status_code,
                response=error.response.text,
            )
        
        else:
            raise RiotAPIError(
                f"Unexpected API error: {error.response.status_code}",
                status_code=error.response.status_code,
                response=error.response.text,
            )
    
    def execute_with_retry(self, func, *args, **kwargs):
        """
        Execute a function with retry logic for rate limiting.
        
        Args:
            func: The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
            
        Returns:
            The result of the function.
            
        Raises:
            RiotAPIRateLimitError: If the rate limit is exceeded after all retry attempts.
            Other exceptions from the function.
        """
        attempts = 0
        while attempts <= self.retry_attempts:
            try:
                return func(*args, **kwargs)
            except ApiError as e:
                if e.response.status_code == self.HTTP_TOO_MANY_REQUESTS:
                    retry_after = int(e.response.headers.get("Retry-After", self.retry_delay))
                    logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds.")
                    
                    if attempts < self.retry_attempts:
                        time.sleep(retry_after)
                        attempts += 1
                        continue
                
                # Handle other API errors
                self._handle_api_error(e)
            
            except Exception as e:
                logger.error(f"Error executing function: {e}")
                raise