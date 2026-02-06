from did.query import Query

def ontology_table_row_vars(session):
    """
    Return all ontologyTableRow document variable names in dataset/session.

    Args:
        session: An NDI session object.

    Returns:
        tuple: (names, variable_names, ontology_nodes)
            names (list): cell array of ontology names available
            variable_names (list): the short name that appears in the table
            ontology_nodes (list): the ontology node names of each variable
    """
    query = Query('', 'isa', 'ontologyTableRow')
    l = session.database_search(query)

    all_names = []
    all_variable_names = []
    all_ontology_nodes = []

    for doc in l:
        props = doc.document_properties.get('ontologyTableRow', {})

        names_str = props.get('names', '')
        variable_names_str = props.get('variableNames', '')
        ontology_nodes_str = props.get('ontologyNodes', '')

        name_list = names_str.split(',') if names_str else []
        variable_names_list = variable_names_str.split(',') if variable_names_str else []
        ontology_nodes_list = ontology_nodes_str.split(',') if ontology_nodes_str else []

        all_names.extend(name_list)
        all_variable_names.extend(variable_names_list)
        all_ontology_nodes.extend(ontology_nodes_list)

    # Use a dictionary to keep unique names and corresponding values
    # Overwriting ensures we keep the last occurrence, mimicking Matlab's unique default behavior
    unique_map = {}
    for n, v, o in zip(all_names, all_variable_names, all_ontology_nodes):
        unique_map[n] = (v, o)

    sorted_names = sorted(unique_map.keys())

    unique_names = sorted_names
    unique_variable_names = [unique_map[n][0] for n in sorted_names]
    unique_ontology_nodes = [unique_map[n][1] for n in sorted_names]

    return unique_names, unique_variable_names, unique_ontology_nodes
