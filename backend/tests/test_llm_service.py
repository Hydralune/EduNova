import unittest
from unittest.mock import patch, Mock
import os
import sys
import requests

# Add the project root to the sys.path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.llm_service import generate_text

class TestLlmService(unittest.TestCase):

    @patch('app.services.llm_service.requests.post')
    def test_generate_text_success(self, mock_post):
        """
        Tests the successful generation of text.
        """
        # Arrange: Mock a successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        prompt_template = "Test prompt for {subject}."
        data = {"subject": "testing"}

        # Act: Call the function
        result = generate_text(prompt_template, data)

        # Assert: Check the result and that the mock was called correctly
        self.assertEqual(result, "This is a test response.")
        
        # Verify the arguments passed to requests.post
        expected_url = "https://api.deepseek.com/chat/completions"
        expected_prompt = "Test prompt for testing."
        
        called_args, called_kwargs = mock_post.call_args
        self.assertEqual(called_args[0], expected_url)
        self.assertIn("Authorization", called_kwargs["headers"])
        self.assertEqual(called_kwargs["json"]["messages"][0]["content"], expected_prompt)
        self.assertEqual(called_kwargs["json"]["model"], "deepseek-chat")


    @patch('app.services.llm_service.requests.post')
    def test_generate_text_api_error(self, mock_post):
        """
        Tests the handling of an API error (e.g., 500 status code).
        """
        # Arrange: Mock a failed API response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("API Error")
        mock_post.return_value = mock_response
        
        prompt_template = "This will fail."
        data = {}

        # Act & Assert: Check that an exception is raised
        with self.assertRaisesRegex(Exception, "API request failed"):
            generate_text(prompt_template, data)

if __name__ == '__main__':
    # This allows running the tests directly from the command line
    unittest.main() 