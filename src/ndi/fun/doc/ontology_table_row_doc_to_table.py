import pandas as pd
from ndi.fun.table import vstack

def ontology_table_row_doc_to_table(table_row_doc, stack_all=False):
    """
    Converts NDI ontologyTableRow documents to pandas DataFrames.

    Args:
        table_row_doc (ndi.document or list of ndi.document): Documents to convert.
        stack_all (bool): Whether to stack all tables together.

    Returns:
        tuple: (data_tables, doc_ids)
            data_tables (list of pd.DataFrame): The extracted tables.
            doc_ids (list of list of str): The corresponding document IDs.
    """
    if not isinstance(table_row_doc, list):
        table_row_doc = [table_row_doc]

    table_rows = []
    variable_names_list = []
    doc_id_list = []

    for doc in table_row_doc:
        props = doc.document_properties['ontologyTableRow']
        data = props['data']
        # Convert to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            # Handle empty or scalar?
            df = pd.DataFrame()

        table_rows.append(df)
        variable_names_list.append(props.get('variableNames'))
        doc_id_list.append(doc.id)

    if stack_all:
        data_tables = [vstack(table_rows)]
        doc_ids = [doc_id_list]
    else:
        # Group by variableNames
        # Need to handle if variableNames is list or str
        def get_key(v):
            if isinstance(v, list):
                return tuple(v)
            return v

        unique_vars = sorted(list(set(get_key(v) for v in variable_names_list)), key=lambda x: str(x))

        data_tables = []
        doc_ids = []

        for var_key in unique_vars:
            # Find indices
            indices = [i for i, v in enumerate(variable_names_list) if get_key(v) == var_key]

            group_tables = [table_rows[i] for i in indices]
            group_ids = [doc_id_list[i] for i in indices]

            data_tables.append(vstack(group_tables))
            doc_ids.append(group_ids)

    return data_tables, doc_ids
