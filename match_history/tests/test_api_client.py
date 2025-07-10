"""
Tests for the Riot API client.
"""
import unittest
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.core.cache import cache

from match_history.services.riot_api.base import RiotAPIClient
from match_history.services.riot_api.exceptions import (
    RiotAPIError,
    RiotAPIRateLimitError,
    RiotAPINotFoundError,
    RiotAPIForbiddenError,
    RiotAPIServerError,
    RiotAPITimeoutError,
    RiotAPIServiceUnavailableError,
)
from match_history.services.riot_api.cache import RiotAPICache


class RiotAPIClientTestCase(TestCase):
    """Test case for the RiotAPIClient class."""
    
    def setUp(self):
        """Set up the test case."""
        self.api_key = "test_api_key"
        self.region = "na1"
        self.platform = "americas"
        self.client = RiotAPIClient(
            api_key=self.api_key,
            region=self.region,
            platform=self.platform
        )
        
        # Clear the cache before each test
        cache.clear()
    
    def test_init(self):
        """Test the initialization of the client."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertEqual(self.client.region, self.region)
        self.assertEqual(self.client.platform, self.platform)
        self.assertEqual(self.client.use_cache, True)
        self.assertEqual(self.client.retry_attempts, RiotAPIClient.DEFAULT_RETRY_ATTEMPTS)
        self.assertEqual(self.client.retry_delay, RiotAPIClient.DEFAULT_RETRY_DELAY)
    
    @patch("requests.request")
    def test_make_request_success(self, mock_request):
        """Test making a successful request."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        # Make the request
        result = self.client._make_request("test/endpoint", {"param": "value"})
        
        # Check the result
        self.assertEqual(result, {"test": "data"})
        
        # Check that the request was made correctly
        mock_request.assert_called_once_with(
            "GET",
            f"https://{self.region}.api.riotgames.com/test/endpoint",
            headers={"X-Riot-Token": self.api_key},
            params={"param": "value"},
            timeout=10
        )
    
    @patch("requests.request")
    def test_make_request_rate_limit(self, mock_request):
        """Test handling rate limiting."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "1"}
        mock_response.text = "Rate limit exceeded"
        mock_request.return_value = mock_response
        
        # Set retry attempts to 0 to avoid waiting
        self.client.retry_attempts = 0
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPIRateLimitError) as context:
            self.client._make_request("test/endpoint")
        
        # Check the exception details
        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(context.exception.response, "Rate limit exceeded")
    
    @patch("requests.request")
    def test_make_request_not_found(self, mock_request):
        """Test handling not found errors."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_request.return_value = mock_response
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPINotFoundError) as context:
            self.client._make_request("test/endpoint")
        
        # Check the exception details
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.response, "Not found")
    
    @patch("requests.request")
    def test_make_request_forbidden(self, mock_request):
        """Test handling forbidden errors."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_request.return_value = mock_response
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPIForbiddenError) as context:
            self.client._make_request("test/endpoint")
        
        # Check the exception details
        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.response, "Forbidden")
    
    @patch("requests.request")
    def test_make_request_server_error(self, mock_request):
        """Test handling server errors."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        mock_request.return_value = mock_response
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPIServerError) as context:
            self.client._make_request("test/endpoint")
        
        # Check the exception details
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.response, "Server error")
    
    @patch("requests.request")
    def test_make_request_service_unavailable(self, mock_request):
        """Test handling service unavailable errors."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = "Service unavailable"
        mock_request.return_value = mock_response
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPIServiceUnavailableError) as context:
            self.client._make_request("test/endpoint")
        
        # Check the exception details
        self.assertEqual(context.exception.status_code, 503)
        self.assertEqual(context.exception.response, "Service unavailable")
    
    @patch("requests.request")
    def test_make_request_unexpected_error(self, mock_request):
        """Test handling unexpected errors."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 418
        mock_response.text = "I'm a teapot"
        mock_request.return_value = mock_response
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPIError) as context:
            self.client._make_request("test/endpoint")
        
        # Check the exception details
        self.assertEqual(context.exception.status_code, 418)
        self.assertEqual(context.exception.response, "I'm a teapot")
    
    @patch("requests.request")
    def test_make_request_timeout(self, mock_request):
        """Test handling timeouts."""
        # Mock the request to raise a timeout
        mock_request.side_effect = requests.exceptions.Timeout()
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPITimeoutError):
            self.client._make_request("test/endpoint")
    
    @patch("requests.request")
    def test_make_request_request_exception(self, mock_request):
        """Test handling request exceptions."""
        # Mock the request to raise a request exception
        mock_request.side_effect = requests.exceptions.RequestException("Request error")
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPIError) as context:
            self.client._make_request("test/endpoint")
        
        # Check the exception details
        self.assertEqual(str(context.exception), "Request error: Request error")
    
    @patch("requests.request")
    def test_make_request_unexpected_exception(self, mock_request):
        """Test handling unexpected exceptions."""
        # Mock the request to raise an unexpected exception
        mock_request.side_effect = Exception("Unexpected error")
        
        # Make the request and check that it raises the correct exception
        with self.assertRaises(RiotAPIError) as context:
            self.client._make_request("test/endpoint")
        
        # Check the exception details
        self.assertEqual(str(context.exception), "Unexpected error: Unexpected error")