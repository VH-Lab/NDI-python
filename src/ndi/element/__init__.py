class Element:
    def __init__(self, session, name, reference, element_subtype, underlying_element, direct, author):
        self.session = session
        self.name = name
        self.reference = reference
        self.element_subtype = element_subtype
        self.underlying_element = underlying_element
        self.direct = direct
        self.author = author
