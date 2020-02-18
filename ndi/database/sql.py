from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Table, Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy import and_, or_
from .base_db import BaseDB
from contextlib import contextmanager
from functools import wraps
from ndi import Experiment, DaqSystem, Probe, Epoch, Channel
from ndi.utils import class_to_collection_name, flatten
from ndi.database.utils import handle_iter, check_ndi_object, listify, check_ndi_objects, update_flatbuffer
from ndi.database.query import Query, AndQuery, OrQuery, CompositeQuery



# =========== #
#  Constants  #
# =========== #

FLATBUFFER_KEY = 'flatbuffer'


# ============ #
#  Decorators  #
# ============ #

def recast_ndi_objects_to_documents(func):
    @wraps(func)
    def decorator(self, ndi_objects, *args, **kwargs):
        items = [ self.create_document_from_ndi_object(o) for o in ndi_objects ]
        func(self, items, *args, **kwargs)
    return decorator

def translate_query(func):
    @wraps(func)
    def decorator(self, *args, query=None, sqla_query=None, **kwargs):
        if isinstance(query, Query):
            query = self.generate_sqla_filter(query)
        elif query is None:
            if sqla_query is not None:
                query = sqla_query
        else:
            raise TypeError(f'{query} must be of type Query or CompositeQuery.')
        return func(self, *args, query=query, **kwargs)
    return decorator

def with_session(func):
    """Handle session instantiation, commit, and close operations for a class method."""
    @wraps(func)
    def decorator(self, *args, session=None, **kwargs):
        if enclosed_session := session is None:
            session = self.Session()
        output = func(self, session, *args, **kwargs)
        if enclosed_session:
            session.commit()
            session.close()
        return output
    return decorator

def with_open_session(func):
    """Handle session setup/teardown as a context manager for a class method."""
    @wraps(func)
    @contextmanager
    def decorator(self, *args, session=None, **kwargs):
        if enclosed_session := session is None:
            session = self.Session()
        yield func(self, session, *args, **kwargs)
        if enclosed_session:
            session.commit()
            session.close()
    return decorator




# ============== #
#  SQL Database  #
# ============== #

class SQL(BaseDB):
    """Interface for SQL Databases.
    
    .. currentmodule:: ndi.database.base_db
    Inherits from the :class:`BaseDB` abstract class.
    """

    relationships = {}

    def __init__(self, connection_string):
        """Sets up a SQL database with collections, binds a sqlAlchemy sessionmaker, and instantiates a slqAlchemy metadata Base.
        
        :param connection_string: A standard SQL Server connection string.
        :type connection_string: str
        """
        self.db = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.db)
        self.Base = declarative_base()
        self.__create_collections(self.__configure_collections())

    @with_open_session
    def _sqla_open_session(self, session):
        """Exposes a session for use in a :code:`'with'` statement.
        ::
            with db._sqla_open_session() as session:
                # session work
        
        Handles session setup, commit, and close. Only for use by developers wanting to access the underlying sqlAlchemy layer.
        
        :param session: Recieved from decorator.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :return: A sqlAlchemy session instance.
        :rtype: Iterator[:class:`sqlalchemy.orm.session.Session`]
        """
        return session

    def execute(self, query):
        """Runs a `sqlAlchemy query <https://docs.sqlalchemy.org/en/13/core/connections.html>`_. Only for use by developers wanting to access the underlying sqlAlchemy layer.
        
        :param query: A SQL query in the format of the given database.
        :type query: str
        """
        return self.db.execute(query)

    def __configure_collections(self):
        """Postponing documentation pending NDI_Collection."""
        return {
            Experiment: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),
                'name': Column(String),
                
                'daq_systems': self.define_relationship(DaqSystem, lazy='joined', cascade='all, delete, delete-orphan'),
            },
            DaqSystem: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),
                'name': Column(String),

                'experiment_id': Column(String, ForeignKey('experiments.id')),
                'experiment': self.define_relationship(Experiment),

                'probes': self.define_relationship(Probe, cascade='all, delete, delete-orphan'),
                'epochs': self.define_relationship(Epoch, cascade='all, delete, delete-orphan'),
                'channels': self.define_relationship(Channel, cascade='all, delete, delete-orphan'),
            },
            Probe: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),
                'name': Column(String),
                'reference': Column(Integer),
                'type': Column(String),

                'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
                'daq_system': self.define_relationship(DaqSystem),

                'channels': self.define_relationship(Channel, cascade='all, delete, delete-orphan'),
            },
            Epoch: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),

                'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
                'daq_system': self.define_relationship(DaqSystem),

                'channels': self.define_relationship(Channel, cascade='all, delete, delete-orphan'),
            },
            Channel: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),
                'name': Column(String),
                'number': Column(Integer),
                'type': Column(String),
                'clock_type': Column(String),
                'source_file': Column(String),

                'probe_id': Column(String, ForeignKey('probes.id')),
                'probe': self.define_relationship(Probe),
                'epoch_id': Column(String, ForeignKey('epochs.id')),
                'epoch': self.define_relationship(Epoch),
                'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
                'daq_system': self.define_relationship(DaqSystem),
            }
        }

    def __get_columns(self, config):
        """Postponing documentation pending NDI_Collection."""
        return { key: item for key, item in config.items() if isinstance(item, Column)}

    def __get_relationships(self, config):
        """Postponing documentation pending NDI_Collection."""
        return { key: item for key, item in config.items() if not isinstance(item, Column)}

    def __create_collections(self, collection_configs):
        """Creates :class:`Collection`\ s from the given configs and adds them to the database.
        Postponing further documentation pending NDI_Collection.
        """
        for ndi_class, config in collection_configs.items():
            columns = self.__get_columns(config)
            self.create_collection(ndi_class, columns, defer_create_all=True)
        self.Base.metadata.create_all(self.db)
        for ndi_class, config in collection_configs.items():
            relationships = self.__get_relationships(config)
            self.set_relationships(ndi_class, relationships)
        self.Base.metadata.create_all(self.db)

    def create_collection(self, ndi_class, fields, defer_create_all=False):
        """Creates a :class:`Collection` and stores it in _collections.

        Postponing further documentation pending NDI_Collection.
        
        :param ndi_class: The NDI Class this collection will be built on. 
            CRUD operations on this database will require this class to specify the table to operate on.
        :type ndi_class: :term:`NDI class`
        :param fields:
        :type fields:

        :Keyword Arguments:
            * **defer_create_all** (*bool, optional*) -- ; If set to :code:`True`, user must manually issue the `CREATE statement(s) <https://docs.sqlalchemy.org/en/13/core/metadata.html#creating-and-dropping-database-tables>`_ for the table. Defaults to :code:`False`\ .

        Returns:
            :class:`Collection`. The table object for the newly created collection.
        """
        self._collections[ndi_class] = Collection(self.Base, self.Session, ndi_class, fields)
        if not defer_create_all:
            self.Base.metadata.create_all(self.db)
        return self._collections[ndi_class]

    @handle_iter
    def drop_collection(self, ndi_class):
        """Drops collection(s) from the database.
        
        
        .. currentmodule:: ndi.ndi_object

        :param ndi_classes: One or many :term:`NDI class`\ es associated with collections(s) in the database.
        :type ndi_classes: List<:class:`NDI_Object`\ > | :class:`NDI_Object`
        """
        for ndi_class in ndi_classes:
            self._collections[ndi_class].table.__table__.drop(self.db)
            self._collections.pop(ndi_class)
    
    def define_relationship(self, ndi_class, **kwargs):
        """.. currentmodule:: ndi.database.sql
        
        Creates an unset :func:`sqlalchemy.orm.relationship` pointing at the given :term:`NDI class`. Set relationships with :func:`SQL.set_relationships`.

        Postponing further documentation pending NDI_Collection.
        
        :param ndi_class: [description]
        :type ndi_class: [type]
        :return: [description]
        :rtype: [type]
        """
        rel = relationship(class_to_collection_name(ndi_class), **kwargs)
        setattr(rel, '_ndi_class', ndi_class)
        return rel

    def set_relationships(self, ndi_class, relationships):
        """Sets one or many relationships on the given :term:`NDI class`.

        Postponing further documentation pending NDI_Collection.
        
        .. currentmodule:: ndi.database.sql

        :param ndi_class: The :term:`NDI class` associated with the :class:`Collection` the relationships are being set to.

        .. currentmodule:: ndi.ndi_object

        :type ndi_class: :class:`NDI_Object`
        :param relationships: The relationship key/value pairs, where keys resolve to backref labels and values are objects created by :func:`SQL.define_relationship`.
        :type relationships: dict
        """
        self._collections[ndi_class].set_relationships(relationships)

    def _get_tables(self):
        """Gets the :term:`SQLA table`\ s in the database.

        .. currentmodule:: ndi.database.sql

        .. note::
           This bypasses the :class:`Collection` layer and is only useful for very specific operations involving the sqlalchemy layer.
        
        :return: NDI class keys and their :term:`SQLA table` values.
        :rtype: dict
        """
        return { ndi_class: collection.table for ndi_class, collection in self._collections.items() }

    def get_table(self, ndi_class):
        """Gets a :term:`SQLA table`.

        .. note::
           This bypasses the :class:`Collection` layer and is only useful for very specific operations involving the sqlalchemy layer.

        .. currentmodule:: ndi.ndi_object
        
        :param ndi_class: The :term:`NDI class` associated with the desired table.
        :type ndi_class: :class:`NDI_Object`
        :return: :term:`SQLA table`
        :rtype: :class:`sqlalchemy.Table`
        """
        collection = self._collections[ndi_class]
        return collection.table
    
    def _get_collection(self, ndi_object):
        """.. currentmodule:: ndi.database.sql

        Gets the :class:`Collection` associated with the :term:`NDI class` of the given :term:`NDI object`.
        
        :param ndi_object:
        :type ndi_object: :term:`NDI object`
        :rtype: :class:`Collection`
        """
        return self._collections[type(ndi_object)]

    def _group_by_collection(self, ndi_objects):
        """Groups an assortment of :term:`NDI object`\ s by their :term:`NDI class`.

        ::
            p1 = Probe(*args, **kwargs)
            p2 = Probe(*args, **kwargs)
            p3 = Probe(*args, **kwargs)

            e1 = Epoch(*args, **kwargs)
            e2 = Epoch(*args, **kwargs)

            db._group_by_collection([p1, e2, p2, p3, e1])
            # returns {Probe: [p1, p2, p3], Epoch: [e2, e1]}
        
        :param ndi_objects:
        :type ndi_objects: List<:term:`NDI object`>
        :rtype: dict
        """
        objects_by_collection = {}
        for ndi_object in ndi_objects:
            Collection = self._get_collection(ndi_object)
            if Collection in objects_by_collection:
                objects_by_collection[Collection].append(ndi_object)
            else:
                objects_by_collection[Collection] = [ndi_object]
        return objects_by_collection


    @listify
    @check_ndi_objects
    def add_experiment(self, experiments):
        """.. currentmodule:: ndi.experiment
        
        Add one or many :class:`Experiment` instances to the database. Extracts its contents to their respective collections (ei. Probes, Channels, etc.).
        
        :param experiment: 
        :type experiment: List<:class:`Experiment`> | :class:`Experiment`
        """
        daq_systems = [ ds for e in experiments for ds in e.daq_systems ]

        def extract_dependants(ds):
            return ( ds.daq_reader.get_probes(),
                     ds.daq_reader.get_epochs(),
                     ds.daq_reader.get_channels() )
        grouped_dependants = zip(*map(extract_dependants, daq_systems))
        flattened_dependants = [ flatten(group) for group in grouped_dependants ]
        probes, epochs, channels = flattened_dependants

        # self.add([*experiments, *daq_systems, *probes, *epochs, *channels], session=session)

        self.add(experiments)
        self.add(daq_systems)
        self.add([*probes, *epochs])
        self.add(channels)

    @listify
    @check_ndi_objects
    def add(self, ndi_objects, session=None):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and adds them to the database. Objects may belong to different :term:`NDI classes`.
        
        :param ndi_object: The object(s) to be added to the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        additions_by_collection = self._group_by_collection(ndi_objects)
        for Collection, ndi_objects in additions_by_collection.items():
            Collection.add(ndi_objects, session=session)
        

    @listify
    @check_ndi_objects
    def update(self, ndi_objects):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. Objects may belong to different :term:`NDI classes`. 
        
        :param ndi_object: The object(s) to be updated in the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        updates_by_collection = self._group_by_collection(ndi_objects)
        for Collection, ndi_objects in updates_by_collection.items():
            Collection.update(ndi_objects)


    @listify
    @check_ndi_objects
    def upsert(self, ndi_objects):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. If an object doesn't have a document representation, it is added to the collection. Objects may belong to different :term:`NDI classes`. 
        
        :param ndi_object: The object(s) to be upserted into the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        upserts_by_collection = self._group_by_collection(ndi_objects)
        for Collection, ndi_objects in upserts_by_collection.items():
            Collection.upsert(ndi_objects)

    @listify
    @check_ndi_objects
    def delete(self, ndi_objects):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and deletes their :term:`document` in the database. Objects may belong to different :term:`NDI classes`. 
        
        :param ndi_object: The object(s) to be removed from the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        deletions_by_collection = self._group_by_collection(ndi_objects)
        for Collection, ndi_objects in deletions_by_collection.items():
            Collection.delete(ndi_objects)

    def find(self, ndi_class, query=None, order_by=None, as_sql_data=False):
        """Extracts all documents matching the given :term:`query` in the specified :term:`collection`.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.base_db`
        :param query: See :term:`query`, defaults to find-all
        :type query: dict, optional
        :param order_by: Field name to order results by. Defaults to None.
        :type order_by: str, optional
        :param as_sql_data: If set to ``True``, find will return contents of SQL table row as a dict; otherwise, will return :term:`NDI object`\ s. Defaults to ``False``.
        :type as_sql_data: bool, optional
        :rtype: List<:term:`NDI object`> | dict
        """
        sqla_field = getattr(self._collections[ndi_class].table, order_by)
        results = self._collections[ndi_class].find(query=query, order_by=sqla_field, as_flatbuffers = not as_sql_data)
        if as_sql_data:
            return results
        else:
            ndi_objects = [ ndi_class.from_flatbuffer(flatbuffer) for flatbuffer in results ]
            return ndi_objects
    
    def update_many(self, ndi_class, query=None, payload={}, order_by=None):
        """Updates all documents matching the given :term:`query` in the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.base_db`
        :param query: See :term:`query`, defaults to update-all
        :type query: dict, optional
        :param payload: Field and update values to be updated, defaults to {}
        :type payload: :term:`payload`, optional
        :param order_by: Field name to order results by. Defaults to None.
        :type order_by: str, optional
        """
        sqla_field = getattr(self._collections[ndi_class].table, order_by)
        results = self._collections[ndi_class].update_many(query=query, payload=payload, order_by=sqla_field)
        ndi_objects = [ ndi_class.from_flatbuffer(flatbuffer) for flatbuffer in results ]
        return ndi_objects
    
    def delete_many(self, ndi_class, query=None):
        """Deletes all documents matching the given :term:`query` in the specified :term:`collection`.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`BaseDB`
        :param query: See :term:`query`, defaults to {}
        :type query: dict, optional
        """
        self._collections[ndi_class].delete_many(query=query)

    def find_by_id(self, ndi_class, id_, as_sql_data=False):
        """Retrieves the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to search.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to extract.
        :type id_: str
        :param as_sql_data: If set to ``True``, find will return contents of SQL table row as a dict; otherwise, will return :term:`NDI object`\ s. Defaults to ``False``.
        :type as_sql_data: bool, optional
        :rtype: :term:`NDI object`
        """
        result = self._collections[ndi_class].find_by_id(id_, as_flatbuffer = not as_sql_data)
        return result if as_sql_data else ndi_class.from_flatbuffer(result)

    def update_by_id(self, ndi_class, id_, payload={}):
        """Updates the :term:`NDI object` with the given id from the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to update.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to update.
        :type id_: str
        :param payload: Field and update values to be updated, defaults to {}
        :type payload: :term:`payload`, optional
        """
        result = self._collections[ndi_class].update_by_id(id_, payload=payload)
        ndi_object = ndi_class.from_flatbuffer(result)
        return ndi_object

    def delete_by_id(self, ndi_class, id_):
        """Deletes the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to delete.
        :type id_: str
        """
        self._collections[ndi_class].delete_by_id(id_)







# ============ #
#  Collection  #
# ============ #

class Collection:
    def __init__(self, Base, Session, ndi_class, fields):
        self.Session = Session
        self.ndi_class = ndi_class
        self.table_name = class_to_collection_name(ndi_class)
        self.table = type(self.table_name, (Base,), {
            '__tablename__': self.table_name,
            **fields
        })
        self.fields = fields
        self.relationship_keys = {}
    
    def set_relationships(self, relationships):
        for key, relation in relationships.items():
            setattr(self.table, key, relation)
            self.relationship_keys[relation._ndi_class] = key

    @listify
    def remove_relationships(self, relationship_keys):
        for key in relationship_keys:
            delattr(self.table, key)

    @with_open_session
    def sqla_open_session(self, session):
        return (session, self.table, self.relationship_keys)


    def _field_is_column(self, key):
        return isinstance(getattr(self.table, key), Column)
    
    def create_document(self, fields):
        return self.table(**fields)

    def create_document_from_ndi_object(self, ndi_object):
        metadata_fields = {
            key: getattr(ndi_object, key)
            for key in self.fields
            if key != FLATBUFFER_KEY 
        }
        fields = {
            FLATBUFFER_KEY: ndi_object.serialize(),
            **metadata_fields
        }
        return self.create_document(fields)
    
    def extract_document_fields(self, documents):
        extract = lambda doc: { 
            key: getattr(doc, key)
            for key in self.fields 
        }
        if isinstance(documents, list):
            return [ extract(doc) for doc in documents ]
        else:
            return extract(documents)

    def extract_flatbuffers(self, documents):
        extract = lambda doc: getattr(doc, FLATBUFFER_KEY)
        if isinstance(documents, list):
            return [ extract(doc) for doc in documents ]
        else:
            return extract(documents)

    _sqla_filter_ops = {
        # composite types
        AndQuery: lambda conditions: and_(*conditions),
        OrQuery: lambda conditions: or_(*conditions),
        # operators
        '==':       lambda field, value: field == value,
        '!=':       lambda field, value: field != value,
        'contains': lambda field, value: field.contains(value),
        'match':    lambda field, value: field.match(value),
        '>':        lambda field, value: field > value,
        '>=':       lambda field, value: field >= value,
        '<':        lambda field, value: field < value,
        '<=':       lambda field, value: field <= value,
        'exists':   lambda field, value: field,
        'in':       lambda field, value: field.in_(value),
    }

    def generate_sqla_filter(self, query):
        def recurse(q):
            if isinstance(q, CompositeQuery):
                nested_queries = [recurse(nested_q) for nested_q in q]
                return self._sqla_filter_ops[type(q)](nested_queries)
            else:
                field, operator, value = q.query
                column = self.fields[field]
                return self._sqla_filter_ops[operator](column, value)
        return recurse(query)

    def _functionalize_query(self, query):
        def filter_(expr):
            return expr if query is None else expr.filter(query)
        return filter_

    @recast_ndi_objects_to_documents
    @with_session
    def add(self, session, items):
        session.add_all(items)

    @recast_ndi_objects_to_documents
    @with_session
    def update(self, session, items):
        q = session.query(self.table)
        for item in items:
            doc = q.get(item.id)
            for key in self.fields:
                setattr(doc, key, getattr(item, key))

    @recast_ndi_objects_to_documents
    @with_session
    def upsert(self, session, items):
        q = session.query(self.table)
        for item in items:
            doc = q.get(item.id)
            if doc is None:
                session.add(item)
            else:
                for key in self.fields:
                    setattr(doc, key, getattr(item, key))
        

    @recast_ndi_objects_to_documents
    @with_session
    def delete(self, session, items):
        for item in items:
            doc = session.query(self.table).get(item.id)
            session.delete(doc)

    @with_session
    @translate_query
    def find(self, session, query=None, order_by=None, as_flatbuffers=True):
        filter_ = self._functionalize_query(query)
        documents = filter_(session.query(self.table)).order_by(order_by).all()
        return self.extract_flatbuffers(documents) if as_flatbuffers else self.extract_document_fields(documents)

    @with_open_session
    @translate_query
    def sqla_find(self, session, query=None, order_by=None):
        filter_ = self._functionalize_query(query)
        return filter_(session.query(self.table)).order_by(order_by).all()

    @with_session
    @translate_query
    def delete_many(self, session, query=None):
        filter_ = self._functionalize_query(query)
        documents = filter_(session.query(self.table)).all()
        for doc in documents:
            session.delete(doc)

    @with_session
    def find_by_id(self, session, id_, as_flatbuffer=True):
        document = session.query(self.table).get(id_)
        return self.extract_flatbuffers(document) if as_flatbuffer else self.extract_document_fields(document)

    @with_session
    def update_by_id(self, session, id_, payload={}):
        document = session.query(self.table).get(id_)
        self.__update_sqla_partial_document(document, payload)
        return self.extract_flatbuffers(document)

    @with_session
    def delete_by_id(self, session, id_):
        document = session.query(self.table).get(id_)
        session.delete(document)

    @with_session
    @translate_query
    def update_many(self, session, query={}, payload={}, order_by=None):
        filter_ = self._functionalize_query(query)
        documents = filter_(session.query(self.table)).order_by(order_by).all()
        for d in documents:
            self.__update_sqla_partial_document(d, payload)
        return self.extract_flatbuffers(documents)

    def __update_sqla_partial_document(self, document, payload):
        # NOT PURE: modifies document in place
        for key, value in payload.items():
            setattr(document, key, value)
        if hasattr(document, FLATBUFFER_KEY):
            old_flatbuffer = getattr(document, FLATBUFFER_KEY)
            updated_flatbuffer = update_flatbuffer(self.ndi_class, old_flatbuffer, payload)
            setattr(document, FLATBUFFER_KEY, updated_flatbuffer)
