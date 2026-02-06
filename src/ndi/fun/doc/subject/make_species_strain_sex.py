def make_species_strain_sex(session, subject_id, biological_sex='', species='', strain='', add_to_session=False):
    """
    Add species, strain, or sex information for a subject in an ndi.session.

    Args:
        session: An ndi.session object.
        subject_id (str): The subject document ID.
        biological_sex (str): 'male', 'female', 'hermaphrodite', or 'notDetectable'.
        species (str): Ontology identifier (e.g. 'NCBITaxon:10116').
        strain (str): Ontology identifier (e.g. 'RRID:RGD_70508').
        add_to_session (bool): Whether to add documents to the session (default False).

    Returns:
        tuple: (ndi_doc_array, openminds_obj)
            ndi_doc_array (list): A list of created ndi.document objects.
            openminds_obj (list): A list of openMINDS objects.

    Raises:
        NotImplementedError: Because it depends on ndi.ontology.lookup and openMINDS support which are not yet ported.
    """
    raise NotImplementedError("This function depends on ndi.ontology.lookup and openMINDS support which are not yet ported.")
