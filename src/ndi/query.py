from did.query import Query

class Query(Query):
    def __init__(self, field, op=None, param1=None, param2=None):
        super().__init__(field, op, param1, param2)
