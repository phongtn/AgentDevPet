#%%
import os
import unittest
from unittest.mock import patch, MagicMock

import httpx

from agno.agent import Agent
from agno.media import ImageArtifact
from pexels import PexelsTools


class TestPexelsTools(unittest.TestCase):
    """Test suite for the PexelsTools class."""

    def setUp(self):
        """Set up a test environment before each test."""
        # Create a mock API key for testing
        self.test_api_key = "test_api_key"
        # Create an instance of the toolkit with the test API key
        self.pexels_tools = PexelsTools(api_key=self.test_api_key, limit=2)
        # Create a mock agent for testing
        self.mock_agent = MagicMock(spec=Agent)

    def test_init_with_api_key(self):
        """Test that the toolkit initializes correctly with an API key."""
        self.assertEqual(self.pexels_tools.api_key, self.test_api_key)
        self.assertEqual(self.pexels_tools.limit, 2)
        self.assertEqual(self.pexels_tools.name, "pexels_tools")

    @patch.dict(os.environ, {"PEXELS_API_KEY": "env_api_key"})
    def test_init_with_env_variable(self):
        """Test that the toolkit initializes correctly with an environment variable."""
        pexels_tools = PexelsTools()
        self.assertEqual(pexels_tools.api_key, "env_api_key")
        self.assertEqual(pexels_tools.limit, 3)  # Default value

    @patch("httpx.get")
    def test_search_photos_success(self, mock_get):
        """Test the search_photos method with a successful API response."""
        # Mock the response from the Pexels API
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "photos": [
                {
                    "id": "photo1",
                    "src": {
                        "original": "https://example.com/photo1.jpg"
                    },
                    "alt": "Photo 1 description"
                },
                {
                    "id": "photo2",
                    "src": {
                        "original": "https://example.com/photo2.jpg"
                    },
                    "alt": "Photo 2 description"
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call the method
        result = self.pexels_tools.search_photos(self.mock_agent, "nature")

        # Verify the API was called with the correct parameters
        mock_get.assert_called_once_with(
            "https://api.pexels.com/v1/search",
            params={"q": "nature", "per_page": 2},
            headers={"Authorization": self.test_api_key}
        )

        # Verify the agent's add_image method was called with the correct parameters
        self.assertEqual(self.mock_agent.add_image.call_count, 2)

        # Get the first call arguments
        args1, kwargs1 = self.mock_agent.add_image.call_args_list[0]
        # Verify the first image was added correctly
        self.assertIsInstance(args1[0], ImageArtifact)
        self.assertEqual(args1[0].url, "https://example.com/photo1.jpg")
        self.assertEqual(args1[0].alt_text, "Photo 1 description")
        self.assertEqual(args1[0].revised_prompt, "nature")

        # Get the second call arguments
        args2, kwargs2 = self.mock_agent.add_image.call_args_list[1]
        # Verify the second image was added correctly
        self.assertIsInstance(args2[0], ImageArtifact)
        self.assertEqual(args2[0].url, "https://example.com/photo2.jpg")
        self.assertEqual(args2[0].alt_text, "Photo 2 description")
        self.assertEqual(args2[0].revised_prompt, "nature")

        # Verify the result contains the expected URLs
        self.assertIn("https://example.com/photo1.jpg", result)
        self.assertIn("https://example.com/photo2.jpg", result)

    @patch("httpx.get")
    def test_search_photos_http_error(self, mock_get):
        """Test the search_photos method with an HTTP error from the API."""
        # Mock an HTTP error response
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=MagicMock(status_code=401, text="Unauthorized")
        )
        mock_get.return_value = mock_response

        # Call the method
        result = self.pexels_tools.search_photos(self.mock_agent, "nature")

        # Verify the result is the default error message
        self.assertEqual(result, "No photo found")

        # Verify add_image was never called
        self.mock_agent.add_image.assert_not_called()

    @patch("httpx.get")
    def test_search_photos_general_exception(self, mock_get):
        """Test the search_photos method with a general exception."""
        # Mock a general exception
        mock_get.side_effect = Exception("General error")

        # Call the method
        result = self.pexels_tools.search_photos(self.mock_agent, "nature")

        # Verify the result is the default error message
        self.assertEqual(result, "No photo found")

        # Verify add_image was never called
        self.mock_agent.add_image.assert_not_called()

    @patch("httpx.get")
    def test_search_photos_empty_response(self, mock_get):
        """Test the search_photos method with an empty response."""
        # Mock an empty response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"photos": []}
        mock_get.return_value = mock_response

        # Call the method
        result = self.pexels_tools.search_photos(self.mock_agent, "nonexistent_query")

        # Verify the result contains the empty list
        self.assertEqual(result, "These are the found photos []")

        # Verify add_image was never called
        self.mock_agent.add_image.assert_not_called()


if __name__ == "__main__":
    unittest.main()