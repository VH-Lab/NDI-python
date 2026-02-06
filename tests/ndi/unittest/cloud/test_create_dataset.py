import unittest
from unittest.mock import patch, Mock
import os
from ndi.cloud.api.datasets.create_dataset import create_dataset

class TestCreateDataset(unittest.TestCase):

    @patch('ndi.cloud.api.implementation.datasets.create_dataset.authenticate')
    @patch('requests.post')
    def test_create_dataset_success(self, mock_post, mock_authenticate):
        """
        Tests the create_dataset function on a successful API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 'new_dataset_id'}
        mock_post.return_value = mock_response

        dataset_info = {'name': 'Test Dataset'}
        success, answer, _, _ = create_dataset(dataset_info, organization_id='org-123')

        self.assertTrue(success)
        self.assertEqual(answer['id'], 'new_dataset_id')

        # Verify call arguments
        # We need to verify that requests.post was called with correct URL and headers
        # But URL depends on implementation details (url.get_url).
        # We can check if mock_post was called.
        mock_post.assert_called()

    @patch('ndi.cloud.api.implementation.datasets.create_dataset.authenticate')
    @patch('requests.post')
    def test_create_dataset_failure(self, mock_post, mock_authenticate):
        """
        Tests the create_dataset function on a failed API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Bad Request'}
        mock_post.return_value = mock_response

        dataset_info = {'name': 'Test Dataset'}
        success, answer, _, _ = create_dataset(dataset_info, organization_id='org-123')

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Bad Request')

if __name__ == '__main__':
    unittest.main()
