import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock 'did' and 'did.query' before importing ndi
mock_did = MagicMock()
sys.modules['did'] = mock_did
sys.modules['did.query'] = mock_did
sys.modules['did.document'] = mock_did

from ndi.cloud.sync.download_new import download_new
from ndi.cloud.sync.sync_options import SyncOptions

class TestCloudSyncDownloadNew(unittest.TestCase):

    def setUp(self):
        self.mock_dataset = MagicMock()
        self.mock_dataset.path = '/tmp/fake_dataset'

    @patch('ndi.cloud.sync.download_new.get_cloud_dataset_id_for_local_dataset')
    @patch('ndi.cloud.sync.download_new.read_sync_index')
    @patch('ndi.cloud.sync.download_new.list_remote_document_ids')
    @patch('ndi.cloud.sync.download_new.download_ndi_documents')
    @patch('ndi.cloud.sync.download_new.list_local_documents')
    @patch('ndi.cloud.sync.download_new.update_sync_index')
    def test_download_new_success(self, mock_update_index, mock_list_local, mock_download_docs, mock_list_remote, mock_read_index, mock_get_cloud_id):
        # Setup mocks
        mock_get_cloud_id.return_value = ('cloud-id-123', [])
        mock_read_index.return_value = {'remoteDocumentIdsLastSync': ['doc1']}
        mock_list_remote.return_value = {'ndiId': ['doc1', 'doc2'], 'apiId': ['api1', 'api2']}

        mock_doc = MagicMock()
        mock_doc.document_properties = {'base': {'id': 'doc2'}}
        mock_download_docs.return_value = [mock_doc]

        mock_list_local.return_value = ([], ['doc1', 'doc2'])

        sync_options = SyncOptions(Verbose=False)

        # Execute
        success, msg, report = download_new(self.mock_dataset, sync_options)

        # Verify
        self.assertTrue(success)
        self.assertEqual(report['downloaded_document_ids'], ['doc2'])

        mock_download_docs.assert_called_once()
        args, _ = mock_download_docs.call_args
        self.assertEqual(args[0], 'cloud-id-123')
        self.assertEqual(args[1], ['api2']) # doc2 is new, corresponds to api2

        mock_update_index.assert_called_once()

    @patch('ndi.cloud.sync.download_new.get_cloud_dataset_id_for_local_dataset')
    @patch('ndi.cloud.sync.download_new.read_sync_index')
    @patch('ndi.cloud.sync.download_new.list_remote_document_ids')
    @patch('ndi.cloud.sync.download_new.download_ndi_documents')
    @patch('ndi.cloud.sync.download_new.update_sync_index')
    def test_download_new_no_changes(self, mock_update_index, mock_download_docs, mock_list_remote, mock_read_index, mock_get_cloud_id):
        mock_get_cloud_id.return_value = ('cloud-id-123', [])
        mock_read_index.return_value = {'remoteDocumentIdsLastSync': ['doc1']}
        mock_list_remote.return_value = {'ndiId': ['doc1'], 'apiId': ['api1']}

        sync_options = SyncOptions(Verbose=False)
        success, msg, report = download_new(self.mock_dataset, sync_options)

        self.assertTrue(success)
        self.assertEqual(report['downloaded_document_ids'], [])
        mock_download_docs.assert_not_called()
        mock_update_index.assert_called_once()

if __name__ == '__main__':
    unittest.main()
