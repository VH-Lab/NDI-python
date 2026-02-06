import unittest
from unittest.mock import patch, Mock
from ndi.cloud.api.documents import add_document, get_document, update_document, delete_document, list_dataset_documents, list_dataset_documents_all

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

    @patch('ndi.cloud.api.implementation.documents.list_dataset_documents.authenticate')
    @patch('requests.get')
    def test_list_dataset_documents_all(self, mock_get, mock_authenticate):
        mock_authenticate.return_value = 'fake_token'

        # Page 1 response
        resp1 = Mock()
        resp1.status_code = 200
        resp1.json.return_value = [{'id': 'doc1'}, {'id': 'doc2'}]

        # Page 2 response (partial page)
        resp2 = Mock()
        resp2.status_code = 200
        resp2.json.return_value = [{'id': 'doc3'}]

        mock_get.side_effect = [resp1, resp2]

        # page_size=2 to force 2 pages
        success, answer, _, _ = list_dataset_documents_all('ds1', page_size=2)

        self.assertTrue(success)
        self.assertEqual(len(answer), 3)
        self.assertEqual(answer[0]['id'], 'doc1')
        self.assertEqual(answer[2]['id'], 'doc3')
        self.assertEqual(mock_get.call_count, 2)

if __name__ == '__main__':
    unittest.main()
