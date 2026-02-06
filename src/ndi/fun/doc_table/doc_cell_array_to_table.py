import pandas as pd
from ndi.fun.table import vstack

def doc_cell_array_to_table(doc_cell_array):
    """
    Converts a cell array of NDI documents to a table, with document IDs.

    Args:
        doc_cell_array (list of ndi.document): List of documents.

    Returns:
        tuple: (data_table, doc_ids)
            data_table (pd.DataFrame): Table with properties.
            doc_ids (list): List of document IDs.
    """
    if not isinstance(doc_cell_array, list):
        doc_cell_array = [doc_cell_array]

    tables = []
    doc_ids = []

    for doc in doc_cell_array:
        tables.append(doc.to_table())
        doc_ids.append(doc.id)

    data_table = vstack(tables) if tables else pd.DataFrame()
    return data_table, doc_ids
