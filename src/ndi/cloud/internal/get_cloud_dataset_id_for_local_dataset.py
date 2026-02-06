from ...query import Query

def get_cloud_dataset_id_for_local_dataset(ndi_dataset):
    """
    Retrieves the cloud dataset ID for a local dataset.
    """
    cloud_dataset_id_query = Query('', 'isa', 'dataset_remote')
    # Assuming database_search returns a list of documents
    cloud_dataset_id_documents = ndi_dataset.database_search(cloud_dataset_id_query)

    if len(cloud_dataset_id_documents) > 1:
        raise RuntimeError(f"Found more than one remote cloudDatasetId for the local dataset: {ndi_dataset.path}.")
    elif cloud_dataset_id_documents:
        # Assuming document structure
        doc = cloud_dataset_id_documents[0]
        return doc.document_properties['dataset_remote']['dataset_id'], cloud_dataset_id_documents
    else:
        return '', []
