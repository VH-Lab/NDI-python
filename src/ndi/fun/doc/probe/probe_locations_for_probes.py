def probe_locations_for_probes(session, probes, ontology_lookup_strings, do_add=True):
    """
    Create and add probe_location documents for a set of probes.

    Args:
        session: An ndi.session object.
        probes (list of ndi.probe.Probe): A list of probe objects.
        ontology_lookup_strings (list of str): Ontology lookup strings.
        do_add (bool): Whether to add the documents to the session database.

    Returns:
        list: A list of ndi.document objects.

    Raises:
        NotImplementedError: Because it depends on ndi.ontology.lookup which is not yet ported.
    """
    raise NotImplementedError("This function depends on ndi.ontology.lookup which is not yet ported.")
