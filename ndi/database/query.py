class Query:
    def __init__(self, field='', queries={}):
        if field:
            if isinstance(field, str):
                self.__field = field
            else:
                raise TypeError(
                    f'The field passed in NDI_Query must be a string')
        self.__queries = queries
        self.__resolved = bool(self.__queries)

    @property
    def queries(self):
        # Query structure
        # Single query structure: {field: (operator, value)}
        # Composite query structure: {conjunction: [query]}
        # >>> a = Query('a') == 1
        # >>> a.queries
        # {'a': ('==', 1)}
        # >>> b = Query('b') / 'two'
        # >>> b.queries
        # {'b': ('contains', 'two')}
        # >>> (a & b).queries
        # {
        #     'and': [
        #         {'a': ('==', 1)},
        #         {'b': ('contains', 'two')}
        #     ]
        # }
        # >>> c = (a | b) & (Query('c') >= 24)
        # >>> c.queries
        # {
        #     'and': [
        #         {
        #             'or': [
        #                 {'a': ('==', 1)},
        #                 {'b': ('contains', 'two')}
        #             ]
        #         },
        #         {'c': ('>=', 24)}
        #     ]
        # }
        if self.__resolved:
            return self.__queries
        else:
            raise SyntaxError(
                f'The query field \'{self.__field}\' has not been resolved yet')

    # Methods for combining ndi_queries
    @classmethod
    def __merge_queries(cls, conjunction, queries):
        return cls(queries={conjunction: queries})

    def __and__(self, ndi_query):
        return self.__merge_queries('and', [self.queries, ndi_query.queries])

    def __or__(self, ndi_query):
        return self.__merge_queries('or', [self.queries, ndi_query.queries])

    # Methods for creating conditional statements
    def __set_filter(self, operator, value):
        if self.__field:
            self.__queries = {self.__field: (operator, value)}
            self.__resolved = True
            return self
        else:
            raise AttributeError('NDI_Query does not have a __field attribute')

    def equals(self, value):
        return self.__set_filter('==', value)

    def __eq__(self, value):
        # Q(field) == value
        return self.equals(value)

    def not_equals(self, value):
        return self.__set_filter('!=', value)

    def __ne__(self, value):
        # Q(field) != value
        return self.not_equals(value)

    def contains(self, value):
        return self.__set_filter('contains', value)

    def __truediv__(self, value):
        # Q(field) / value
        return self.contains(value)

    def match(self, value):
        return self.__set_filter('match', value)

    def __getitem__(self, value):
        # Q(field)[value]
        return self.match(value)

    def greater_than(self, value):
        return self.__set_filter('>', value)

    def __gt__(self, value):
        # Q(field) > value
        return self.greater_than(value)

    def greater_than_or_equal_to(self, value):
        return self.__set_filter('>=', value)

    def __ge__(self, value):
        # Q(field) >= value
        return self.greater_than_or_equal_to(value)

    def less_than(self, value):
        return self.__set_filter('<', value)

    def __lt__(self, value):
        # Q(field) < value
        return self.less_than(value)

    def less_than_or_equal_to(self, value):
        return self.__set_filter('<=', value)

    def __le__(self, value):
        # Q(field) <= value
        return self.less_than_or_equal_to(value)

    def exists(self, value=True):
        return self.__set_filter('exists', value)

    def __pos__(self):
        # +Q(field)
        return self.exists(True)

    def __neg__(self):
        # -Q(field)
        return self.exists(False)
