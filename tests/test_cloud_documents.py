import unittest
from unittest.mock import patch, Mock
from ndi.cloud.api.documents import add_document, get_document, update_document, delete_document, list_dataset_documents

class TestCloudDocuments(unittest.TestCase):

    @patch('ndi.cloud.api.implementation.documents.add_document.authenticate')
    @patch('requests.post')
    def test_add_document(self, mock_post, mock_authenticate):
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'doc1'}
        mock_post.return_value = mock_response

        success, answer, _, _ = add_document('ds1', {'name': 'doc'})
        self.assertTrue(success)
        self.assertEqual(answer['id'], 'doc1')

    @patch('ndi.cloud.api.implementation.documents.get_document.authenticate')
    @patch('requests.get')
    def test_get_document(self, mock_get, mock_authenticate):
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'doc1'}
        mock_get.return_value = mock_response

        success, answer, _, _ = get_document('ds1', 'doc1')
        self.assertTrue(success)
        self.assertEqual(answer['id'], 'doc1')

    @patch('ndi.cloud.api.implementation.documents.update_document.authenticate')
    @patch('requests.put')
    def test_update_document(self, mock_put, mock_authenticate):
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'doc1'}
        mock_put.return_value = mock_response

        success, answer, _, _ = update_document('ds1', 'doc1', {'name': 'new'})
        self.assertTrue(success)

    @patch('ndi.cloud.api.implementation.documents.delete_document.authenticate')
    @patch('requests.delete')
    def test_delete_document(self, mock_delete, mock_authenticate):
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'deleted'}
        mock_delete.return_value = mock_response

        success, answer, _, _ = delete_document('ds1', 'doc1')
        self.assertTrue(success)

    @patch('ndi.cloud.api.implementation.documents.list_dataset_documents.authenticate')
    @patch('requests.get')
    def test_list_dataset_documents(self, mock_get, mock_authenticate):
        mock_authenticate.return_value = 'fake_token'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'id': 'doc1'}]
        mock_get.return_value = mock_response

        success, answer, _, _ = list_dataset_documents('ds1')
        self.assertTrue(success)
        self.assertEqual(len(answer), 1)

if __name__ == '__main__':
    unittest.main()
