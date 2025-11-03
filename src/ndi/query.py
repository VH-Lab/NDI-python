from did.query import Query as DIDQuery

class Query(DIDQuery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
