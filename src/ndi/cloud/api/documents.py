from .implementation.documents.add_document import AddDocument as AddDocumentImpl
from .implementation.documents.get_document import GetDocument as GetDocumentImpl
from .implementation.documents.update_document import UpdateDocument as UpdateDocumentImpl
from .implementation.documents.delete_document import DeleteDocument as DeleteDocumentImpl
from .implementation.documents.list_dataset_documents import ListDatasetDocuments as ListDatasetDocumentsImpl

def add_document(dataset_id, document_info):
    """
    Adds a document to a dataset.

    Args:
        dataset_id (str): The ID of the dataset.
        document_info (dict): The document information to add.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = AddDocumentImpl(dataset_id, document_info)
    return api_call.execute()

def get_document(dataset_id, document_id):
    """
    Gets a document from a dataset.

    Args:
        dataset_id (str): The ID of the dataset.
        document_id (str): The ID of the document.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = GetDocumentImpl(dataset_id, document_id)
    return api_call.execute()

def update_document(dataset_id, document_id, document_info):
    """
    Updates a document in a dataset.

    Args:
        dataset_id (str): The ID of the dataset.
        document_id (str): The ID of the document.
        document_info (dict): The updated document information.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = UpdateDocumentImpl(dataset_id, document_id, document_info)
    return api_call.execute()

def delete_document(dataset_id, document_id):
    """
    Deletes a document from a dataset.

    Args:
        dataset_id (str): The ID of the dataset.
        document_id (str): The ID of the document.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = DeleteDocumentImpl(dataset_id, document_id)
    return api_call.execute()

def list_dataset_documents(dataset_id, page=1, page_size=20):
    """
    Lists documents in a dataset.

    Args:
        dataset_id (str): The ID of the dataset.
        page (int, optional): The page number. Defaults to 1.
        page_size (int, optional): The number of documents per page. Defaults to 20.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = ListDatasetDocumentsImpl(dataset_id, page, page_size)
    return api_call.execute()
