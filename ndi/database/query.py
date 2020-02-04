class Query:
    def __init__(self, field):
        if isinstance(field, str):
            self.field = field
        else:
            raise TypeError(f'The field passed in NDI_Query must be a string')
        self.__resolved = False

    def __call__(self):
        if self.__resolved:
            return self.__query
        else:
            raise SyntaxError(
                f'The query field \'{self.field}\' has not been resolved yet')

    def __repr__(self):
        return f'<Query {self()}>'
    
    # Methods for combining ndi_queries
    def __and__(self, ndi_query):
        return AndQuery([self, ndi_query])

    def __or__(self, ndi_query):
        return OrQuery([self, ndi_query])

    # Methods for creating conditional statements
    def __set_condition(self, operator, value):
        if not self.__resolved:
            self.operator = operator
            self.value = value
            self.__query = (self.field, operator, value)
            self.__resolved = True
            return self
        else:
            raise SyntaxError(f'This query has already been resolved')

    def equals(self, value):
        return self.__set_condition('==', value)

    def __eq__(self, value):
        # Q(field) == value
        return self.equals(value)

    def not_equals(self, value):
        return self.__set_condition('!=', value)

    def __ne__(self, value):
        # Q(field) != value
        return self.not_equals(value)

    def contains(self, value):
        return self.__set_condition('contains', value)

    def __truediv__(self, value):
        # Q(field) / value
        return self.contains(value)

    def match(self, value):
        return self.__set_condition('match', value)

    def __getitem__(self, value):
        # Q(field)[value]
        return self.match(value)

    def greater_than(self, value):
        return self.__set_condition('>', value)

    def __gt__(self, value):
        # Q(field) > value
        return self.greater_than(value)

    def greater_than_or_equal_to(self, value):
        return self.__set_condition('>=', value)

    def __ge__(self, value):
        # Q(field) >= value
        return self.greater_than_or_equal_to(value)

    def less_than(self, value):
        return self.__set_condition('<', value)

    def __lt__(self, value):
        # Q(field) < value
        return self.less_than(value)

    def less_than_or_equal_to(self, value):
        return self.__set_condition('<=', value)

    def __le__(self, value):
        # Q(field) <= value
        return self.less_than_or_equal_to(value)

    def exists(self, value=True):
        return self.__set_condition('exists', value)

    def __pos__(self):
        # +Q(field)
        return self.exists(True)

    def __neg__(self):
        # -Q(field)
        return self.exists(False)

class CompositeQuery(Query):
    def __init__(self, queries):
        self._queries = queries

    def __iter__(self):
        return iter(self._queries)


class AndQuery(CompositeQuery):
    def __init__(self, queries):
        super().__init__(queries)

    def __and__(self, ndi_query):
        if isinstance(ndi_query, AndQuery):
            self._queries = [*self._queries, *ndi_query()]
        else:
            self._queries.append(ndi_query)
        return self

    def __or__(self, ndi_query):
        if isinstance(ndi_query, OrQuery):
            return OrQuery([self, *ndi_query()])
        else:
            return OrQuery([self, ndi_query])

    def __repr__(self):
        return f'<AndQuery {self._queries}>'


class OrQuery(CompositeQuery):
    def __init__(self, queries):
        super().__init__(queries)

    def __and__(self, ndi_query):
        if isinstance(ndi_query, AndQuery):
            return AndQuery([self, *ndi_query()])
        else:
            return AndQuery([self, ndi_query])

    def __or__(self, ndi_query):
        if isinstance(ndi_query, OrQuery):
            self._queries = [*self._queries, *ndi_query()]
        else:
            self._queries.append(ndi_query)
        return self

    def __repr__(self):
        return f'<OrQuery {self._queries}>'
