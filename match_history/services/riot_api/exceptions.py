"""
Exceptions for the Riot API service.
"""


class RiotAPIError(Exception):
    """Base exception for Riot API errors."""
    
    def __init__(self, message, status_code=None, response=None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class RiotAPIRateLimitError(RiotAPIError):
    """Exception raised when the Riot API rate limit is exceeded."""
    pass


class RiotAPINotFoundError(RiotAPIError):
    """Exception raised when a resource is not found."""
    pass


class RiotAPIForbiddenError(RiotAPIError):
    """Exception raised when the API key is invalid or has insufficient permissions."""
    pass


class RiotAPIServerError(RiotAPIError):
    """Exception raised when the Riot API server returns an error."""
    pass


class RiotAPITimeoutError(RiotAPIError):
    """Exception raised when a request to the Riot API times out."""
    pass


class RiotAPIServiceUnavailableError(RiotAPIError):
    """Exception raised when the Riot API service is unavailable."""
    pass


class RiotAPICacheError(RiotAPIError):
    """Exception raised when there is an error with the cache."""
    pass