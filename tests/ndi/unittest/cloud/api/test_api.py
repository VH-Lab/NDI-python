import unittest
from unittest.mock import patch, Mock
import os
from ndi.cloud.api import url
from ndi.cloud.api.auth.login import login
from ndi.cloud.api.auth.logout import logout
from ndi.cloud.api.auth.change_password import change_password
from ndi.cloud.api.auth.resend_confirmation import resend_confirmation
from ndi.cloud.api.auth.reset_password import reset_password
from ndi.cloud.api.auth.verify_user import verify_user
from ndi.cloud.api.datasets.get_published import get_published
from ndi.cloud.api.datasets.get_unpublished import get_unpublished
from ndi.cloud.api.datasets.list_datasets import list_datasets

class TestCloudApi(unittest.TestCase):

    def test_get_url_prod(self):
        """
        Tests the get_url function in the production environment.
        """
        os.environ['CLOUD_API_ENVIRONMENT'] = 'prod'
        test_url = url.get_url('login')
        self.assertEqual(test_url, "https://api.ndi-cloud.com/v1/auth/login")

    def test_get_url_dev(self):
        """
        Tests the get_url function in the development environment.
        """
        os.environ['CLOUD_API_ENVIRONMENT'] = 'dev'
        test_url = url.get_url('login')
        self.assertEqual(test_url, "https://dev-api.ndi-cloud.com/v1/auth/login")

    def test_get_url_with_params(self):
        """
        Tests the get_url function with path parameters.
        """
        os.environ['CLOUD_API_ENVIRONMENT'] = 'prod'
        test_url = url.get_url('get_user', user_id='123')
        self.assertEqual(test_url, "https://api.ndi-cloud.com/v1/users/123")

    def test_get_url_missing_param(self):
        """
        Tests that get_url raises a ValueError when a required parameter is missing.
        """
        with self.assertRaises(ValueError):
            url.get_url('get_user')

    @patch('requests.post')
    def test_login_success(self, mock_post):
        """
        Tests the login function on a successful API call.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'token': 'fake_token'}
        mock_post.return_value = mock_response

        success, answer, _, _ = login('test@example.com', 'password')

        self.assertTrue(success)
        self.assertEqual(answer['token'], 'fake_token')

    @patch('requests.post')
    def test_login_failure(self, mock_post):
        """
        Tests the login function on a failed API call.
        """
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Invalid credentials'}
        mock_post.return_value = mock_response

        success, answer, _, _ = login('test@example.com', 'password')

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Invalid credentials')

    @patch('ndi.cloud.api.implementation.auth.logout.authenticate')
    @patch('requests.post')
    def test_logout_success(self, mock_post, mock_authenticate):
        """
        Tests the logout function on a successful API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'Logout successful'}
        mock_post.return_value = mock_response

        success, answer, _, _ = logout()

        self.assertTrue(success)
        self.assertEqual(answer['message'], 'Logout successful')

    @patch('ndi.cloud.api.implementation.auth.logout.authenticate')
    @patch('requests.post')
    def test_logout_failure(self, mock_post, mock_authenticate):
        """
        Tests the logout function on a failed API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Invalid token'}
        mock_post.return_value = mock_response

        success, answer, _, _ = logout()

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Invalid token')

    @patch('ndi.cloud.api.implementation.auth.change_password.authenticate')
    @patch('requests.post')
    def test_change_password_success(self, mock_post, mock_authenticate):
        """
        Tests the change_password function on a successful API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'Password changed successfully'}
        mock_post.return_value = mock_response

        success, answer, _, _ = change_password('old_password', 'new_password')

        self.assertTrue(success)
        self.assertEqual(answer['message'], 'Password changed successfully')

    @patch('ndi.cloud.api.implementation.auth.change_password.authenticate')
    @patch('requests.post')
    def test_change_password_failure(self, mock_post, mock_authenticate):
        """
        Tests the change_password function on a failed API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Invalid old password'}
        mock_post.return_value = mock_response

        success, answer, _, _ = change_password('old_password', 'new_password')

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Invalid old password')

    @patch('requests.post')
    def test_resend_confirmation_success(self, mock_post):
        """
        Tests the resend_confirmation function on a successful API call.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'Confirmation email sent'}
        mock_post.return_value = mock_response

        success, answer, _, _ = resend_confirmation('test@example.com')

        self.assertTrue(success)
        self.assertEqual(answer['message'], 'Confirmation email sent')

    @patch('requests.post')
    def test_resend_confirmation_failure(self, mock_post):
        """
        Tests the resend_confirmation function on a failed API call.
        """
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Invalid email'}
        mock_post.return_value = mock_response

        success, answer, _, _ = resend_confirmation('test@example.com')

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Invalid email')

    @patch('ndi.cloud.api.implementation.auth.reset_password.authenticate')
    @patch('requests.post')
    def test_reset_password_success(self, mock_post, mock_authenticate):
        """
        Tests the reset_password function on a successful API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'Password reset email sent'}
        mock_post.return_value = mock_response

        success, answer, _, _ = reset_password('test@example.com')

        self.assertTrue(success)
        self.assertEqual(answer['message'], 'Password reset email sent')

    @patch('ndi.cloud.api.implementation.auth.reset_password.authenticate')
    @patch('requests.post')
    def test_reset_password_failure(self, mock_post, mock_authenticate):
        """
        Tests the reset_password function on a failed API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Invalid email'}
        mock_post.return_value = mock_response

        success, answer, _, _ = reset_password('test@example.com')

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Invalid email')

    @patch('ndi.cloud.api.implementation.auth.verify_user.authenticate')
    @patch('requests.post')
    def test_verify_user_success(self, mock_post, mock_authenticate):
        """
        Tests the verify_user function on a successful API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'User verified'}
        mock_post.return_value = mock_response

        success, answer, _, _ = verify_user('test@example.com', '123456')

        self.assertTrue(success)
        self.assertEqual(answer['message'], 'User verified')

    @patch('ndi.cloud.api.implementation.auth.verify_user.authenticate')
    @patch('requests.post')
    def test_verify_user_failure(self, mock_post, mock_authenticate):
        """
        Tests the verify_user function on a failed API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'error': 'Invalid confirmation code'}
        mock_post.return_value = mock_response

        success, answer, _, _ = verify_user('test@example.com', '123456')

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Invalid confirmation code')

    @patch('ndi.cloud.api.implementation.datasets.get_published.authenticate')
    @patch('requests.get')
    def test_get_published_success(self, mock_get, mock_authenticate):
        """
        Tests the get_published function on a successful API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'name': 'dataset1'}, {'name': 'dataset2'}]
        mock_get.return_value = mock_response

        success, answer, _, _ = get_published()

        self.assertTrue(success)
        self.assertEqual(len(answer), 2)

    @patch('ndi.cloud.api.implementation.datasets.get_published.authenticate')
    @patch('requests.get')
    def test_get_published_failure(self, mock_get, mock_authenticate):
        """
        Tests the get_published function on a failed API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Unauthorized'}
        mock_get.return_value = mock_response

        success, answer, _, _ = get_published()

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Unauthorized')

    @patch('ndi.cloud.api.implementation.datasets.get_unpublished.authenticate')
    @patch('requests.get')
    def test_get_unpublished_success(self, mock_get, mock_authenticate):
        """
        Tests the get_unpublished function on a successful API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'name': 'dataset3'}, {'name': 'dataset4'}]
        mock_get.return_value = mock_response

        success, answer, _, _ = get_unpublished()

        self.assertTrue(success)
        self.assertEqual(len(answer), 2)

    @patch('ndi.cloud.api.implementation.datasets.get_unpublished.authenticate')
    @patch('requests.get')
    def test_get_unpublished_failure(self, mock_get, mock_authenticate):
        """
        Tests the get_unpublished function on a failed API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Unauthorized'}
        mock_get.return_value = mock_response

        success, answer, _, _ = get_unpublished()

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Unauthorized')

    @patch('ndi.cloud.api.implementation.datasets.list_datasets.authenticate')
    @patch('requests.get')
    def test_list_datasets_success(self, mock_get, mock_authenticate):
        """
        Tests the list_datasets function on a successful API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'datasets': [{'name': 'dataset5'}, {'name': 'dataset6'}]}
        mock_get.return_value = mock_response

        success, answer, _, _ = list_datasets(cloud_organization_id='org-123')

        self.assertTrue(success)
        self.assertEqual(len(answer), 2)

    @patch('ndi.cloud.api.implementation.datasets.list_datasets.authenticate')
    @patch('requests.get')
    def test_list_datasets_failure(self, mock_get, mock_authenticate):
        """
        Tests the list_datasets function on a failed API call.
        """
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'error': 'Unauthorized'}
        mock_get.return_value = mock_response

        success, answer, _, _ = list_datasets(cloud_organization_id='org-123')

        self.assertFalse(success)
        self.assertEqual(answer['error'], 'Unauthorized')


if __name__ == '__main__':
    unittest.main()
