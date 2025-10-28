from did.document import Document

class Document(Document):
    def __init__(self, document_type, **options):
        super().__init__(document_type, **options)

    def add_dependency(self, name, value):
        super().add_dependency(name, value)

    def get_dependency_value(self, dependency_name, error_if_not_found=True):
        return super().get_dependency_value(dependency_name, error_if_not_found)

    def set_dependency_value(self, dependency_name, value, error_if_not_found=True):
        super().set_dependency_value(dependency_name, value, error_if_not_found)

    def add_dependency_value_n(self, dependency_name, value):
        super().add_dependency_value_n(dependency_name, value)

    def remove_dependency_value_n(self, dependency_name, n, error_if_not_found=True):
        super().remove_dependency_value_n(dependency_name, n, error_if_not_found)
