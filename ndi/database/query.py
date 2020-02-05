class Query:
    """Class used to create Query objects for querying a database"""

    def __init__(self, field):
        """Starts a query object

        :param field: A field to query the database
        :type field: str
        :raises TypeError: When field is not a str
        """
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
    def and_(self, ndi_query):
        """Combines query objects with :class:`AndQuery`

        a = Query('a') == 'apple'

        b = Query('b') == 'bear'

        c = a.and_(b)

        Can also be written as:

        c = a & b

        :param ndi_query: 
        :type ndi_query: :class:`Query`
        :return: 
        :rtype: :class:`AndQuery`
        """
        return AndQuery([self, ndi_query])

    def __and__(self, ndi_query):
        return self.and_(ndi_query)

    def or_(self, ndi_query):
        """Combines query objects with :class:`OrQuery`
        
        a = Query('a') == 'apple'

        b = Query('b') == 'bear'

        c = a.or_(b)

        Can also be written as:

        c = a | b

        :param ndi_query: 
        :type ndi_query: :class:`Query`
        :return: 
        :rtype: :class:`OrQuery`
        """
        return OrQuery([self, ndi_query])

    def __or__(self, ndi_query):
        return self.or_(ndi_query)

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
        """Creates an 'equals' condition for the specified field
        
        a = Query('a').equals('apple')

        Can also be written as:

        a = Query('a') == 'apple'

        :param value: A value for the field to equal in the database
        :type value: str or number
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('==', value)

    def __eq__(self, value):
        # Q(field) == value
        return self.equals(value)

    def not_equals(self, value):
        """Creates a 'not-equals' condition for the specified field

        a = Query('a').not_equals('apple')

        Can also be written as:

        a = Query('a') != 'apple'

        :param value: A value for the field to not-equal in the database
        :type value: str or number
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('!=', value)

    def __ne__(self, value):
        # Q(field) != value
        return self.not_equals(value)

    def contains(self, value):
        """Creates a 'contains' condition for the specified field

        a = Query('a').contains('apple')

        Can also be written as:

        a = Query('a') / 'apple'

        :param value: A string for the field to contain in the database
        :type value: str
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('contains', value)

    def __truediv__(self, value):
        # Q(field) / value
        return self.contains(value)

    def match(self, value):
        """Creates a regex 'match' condition for the specified field

        a = Query('a').match(r'^[a-z]{5}$')

        Can also be written as:

        a = Query('a')[r'^[a-z]{5}$']

        :param value: A regex expression for the field to match in the database
        :type value: regexp
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('match', value)

    def __getitem__(self, value):
        # Q(field)[value]
        return self.match(value)

    def greater_than(self, value):
        """Creates a 'greater-than' condition for the specified field
        
        a = Query('a').greater_than(5)

        Can also be written as:

        a = Query('a') > 5

        :param value: A number for the field to be greater than in the database
        :type value: number
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('>', value)

    def __gt__(self, value):
        # Q(field) > value
        return self.greater_than(value)

    def greater_than_or_equal_to(self, value):
        """Creates a 'greater-than-or-equal-to' condition for the specified field

        a = Query('a').greater_than_or_equal_to(5)

        Can also be written as:

        a = Query('a') >= 5

        :param value: A number for the field to be greater than or equal to in the database
        :type value: number
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('>=', value)

    def __ge__(self, value):
        # Q(field) >= value
        return self.greater_than_or_equal_to(value)

    def less_than(self, value):
        """Creates a 'less-than' condition for the specified field

        a = Query('a').less_than(5)

        Can also be written as:

        a = Query('a') < 5

        :param value: A number for the field to be less than in the database
        :type value: number
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('<', value)

    def __lt__(self, value):
        # Q(field) < value
        return self.less_than(value)

    def less_than_or_equal_to(self, value):
        """Creates a 'less-than-or-equal-to' condition for the specified field

        a = Query('a').less_than_or_equal_to(5)

        Can also be written as:

        a = Query('a') <= 5

        :param value: A number for the field to be less than or equal to in the database
        :type value: number
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('<=', value)

    def __le__(self, value):
        # Q(field) <= value
        return self.less_than_or_equal_to(value)

    def exists(self, value=True):
        """Creates an 'exists' condition for the specified field

        To check for the existence of a field:

        a = Query('a').exists()

        a = Query('a').exists(True)

        a = +Query('a')

        To check for non-existence of a field

        a = Query('a').exists(False)

        a = +Query('a')

        :param value: A boolean for the field to exist in the database
        :type value: bool (optional, defaults to True)
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('exists', value)

    def __pos__(self):
        # +Q(field)
        return self.exists(True)

    def __neg__(self):
        # -Q(field)
        return self.exists(False)

    def in_(self, value):
        """Creates an 'in' condition for the specified field

        Checks if a field value is in a list of values
        
        To check for the existence of a field:
        
        a = Query('a').in_(['apple', 'ant', 'aardvark'])

        Can also be written as:

        a = Query('a') >> ['apple', 'ant', 'aardvark']

        :param value: A list of for the field to exist in the database
        :type value: [str or number]
        :return: Completed (resolved) query instance
        :rtype: :class:`Query`
        """
        return self.__set_condition('in', value)

    def __rshift__(self, value):
        return self.in_(value)


class CompositeQuery:
    __class__ = Query

    def __init__(self, queries):
        self._queries = queries

    def __iter__(self):
        return iter(self._queries)

    def __repr__(self):
        return f'<{type(self).__name__} {self._queries}>'


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


class OrQuery(CompositeQuery):
    def __init__(self, queries):
        super().__init__(queries)

    def and_(self, ndi_query):
        if isinstance(ndi_query, AndQuery):
            return AndQuery([self, *ndi_query()])
        else:
            return AndQuery([self, ndi_query])

    def __and__(self, ndi_query):
        return self.and_(ndi_query)

    def or_(self, ndi_query):
        if isinstance(ndi_query, OrQuery):
            self._queries = [*self._queries, *ndi_query()]
        else:
            self._queries.append(ndi_query)
        return self

    def __or__(self, ndi_query):
        return self.or_(ndi_query)
