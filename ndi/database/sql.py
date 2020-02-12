from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy import and_, or_
from .base_db import BaseDB
from contextlib import contextmanager
from functools import wraps
from ndi import Experiment, DaqSystem, Probe, Epoch, Channel
from ndi.utils import class_to_collection_name, flatten
from ndi.database.utils import handle_iter, check_ndi_object, listify, check_ndi_objects
from ndi.database.query import Query, AndQuery, OrQuery, CompositeQuery

class SQL(BaseDB):
    """Interface for SQL Databases.
    
    .. currentmodule:: ndi.database.base_db
    Inherits from the :class:`BaseDB` abstract class.
    """

    def __init__(self, connection_string):
        """Sets up a SQL database with collections and binds a sqlAlchemy sessionmaker.
        
        :param connection_string: A standard SQL Server connection string.
        :type connection_string: str
        """
        self.db = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.db)
        self.Base = declarative_base()
        self.__create_collections()

    def execute(self, query):
        """Runs a custom sql query.
        
        :param query: A SQL query in the format of the given database.
        :type query: str
        """
        self.db.execute(query)

    _collections_columns = {
        Experiment: {
            'id': Column(String, primary_key=True),
            'flatbuffer': Column(LargeBinary),
            'name': Column(String),
        },
        DaqSystem: {
            'id': Column(String, primary_key=True),
            'flatbuffer': Column(LargeBinary),
            'experiment_id': Column(String, ForeignKey('experiments.id')),
            'name': Column(String),
        },
        Probe: {
            'id': Column(String, primary_key=True),
            'flatbuffer': Column(LargeBinary),
            'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
            'name': Column(String),
            'reference': Column(Integer),
            'type': Column(String),
        },
        Epoch: {
            'id': Column(String, primary_key=True),
            'flatbuffer': Column(LargeBinary),
            'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
        },
        Channel: {
            'id': Column(String, primary_key=True),
            'flatbuffer': Column(LargeBinary),
            'probe_id': Column(String, ForeignKey('probes.id')),
            'epoch_id': Column(String, ForeignKey('epochs.id')),
            'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
            'name': Column(String),
            'number': Column(Integer),
            'type': Column(String),
            'clock_type': Column(String),
            'source_file': Column(String),
        }
    }

    def get_tables(self):
        return self.Base.metadata.sorted_tables

    def __create_collections(self):
        """Create Base Collections described in :class:`ndi.database.BaseDB`."""
        for collection, columns in self._collections_columns.items():
            self.create_collection(collection, columns, defer_create_all=True)
        self.Base.metadata.create_all(self.db)

    def create_collection(self, ndi_class, fields, defer_create_all=False):
        """Creates a table given an ndi_object and the desired fields and stores it in _collections.
        
        Args:
            ndi_class(:class:`ndi.ndi_class`): The NDI Class this collection will be built on. 
                CRUD operations on this database will require this class to specify the table to operate on.

        Kwargs:
            field_name (:class:`sqlalchemy.Column`): The sqlAlchemy ORM Column instance that defines the given field_name.
                Multiple field_name=Column() arguments may be given for multiple fields.

        Returns:
            :class:`ndi.database.sql.Table`. The table object for the newly created collection.
        """
        self._collections[ndi_class] = Collection(self.Base, self.Session, ndi_class, fields)
        if not defer_create_all:
            self.Base.metadata.create_all(self.db)
        return self._collections[ndi_class]

    def _group_by_collection(self, ndi_objects):
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
        """Add an NDI Experiment Object to the database.
        
        :param experiment: NDI Experiment Object
        :type experiment: :class:`ndi.Experiment`
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


    @handle_iter
    @check_ndi_object
    def upsert(self, ndi_object):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. If an object doesn't have a document representation, it is added to the collection. Objects may belong to different :term:`NDI classes`. 
        
        :param ndi_object: The object(s) to be upserted into the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self._collections[type(ndi_object)]

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

    def find(self, ndi_class, query=None):
        """Extracts all documents matching the given :term:`query` in the specified :term:`collection`.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.base_db`
        :param query: See :term:`query`, defaults to find-all
        :type query: dict, optional
        :rtype: List<:term:`NDI object`>
        """
        flatbuffers = self._collections[ndi_class].find(query=query)
        ndi_objects = [ ndi_class.from_flatbuffer(fb) for fb in flatbuffers ]
        return ndi_objects
    
    def update_many(self, ndi_class, query={}, payload={}):
        """Updates all documents matching the given :term:`query` in the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.base_db`
        :param query: See :term:`query`, defaults to update-all
        :type query: dict, optional
        :param payload: Field and update values to be updated, defaults to {}
        :type payload: :term:`payload`, optional
        """
        self._collections[ndi_class]
    
    def delete_many(self, ndi_class, query={}):
        """Deletes all documents matching the given :term:`query` in the specified :term:`collection`.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`BaseDB`
        :param query: See :term:`query`, defaults to {}
        :type query: dict, optional
        """
        self._collections[ndi_class]

    def find_by_id(self, ndi_class, id_):
        """Retrieves the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to search.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to extract.
        :type id_: str
        :rtype: :term:`NDI object`
        """
        return self._collections[ndi_class]

    def update_by_id(self, ndi_class, id_, payload={}):
        """Updates the :term:`NDI object` with the given id from the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to update.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to update.
        :type id_: str
        """
        self._collections[ndi_class]

    def delete_by_id(self, ndi_class, id_):
        """Deletes the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to delete.
        :type id_: str
        """
        self._collections[ndi_class]

    def _get_collection(self, ndi_object):
        return self._collections[type(ndi_object)]


def recast_ndi_objects_to_documents(func):
    @wraps(func)
    def decorator(self, ndi_objects, *args, **kwargs):
        items = list(map(self.create_document_from_ndi_object, ndi_objects))
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
            else: pass
        else:
            raise TypeError(f'{query} must be of type Query or CompositeQuery.')
        return func(self, *args, query=query, **kwargs)
    return decorator

def with_session(func):
    """Handle session instantiation, commit, and close operations for a class method."""
    @wraps(func)
    def decorator(self, *args, session=None, **kwargs):
        enclosed_session = session is None
        if enclosed_session: 
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
        enclosed_session = session is None
        if enclosed_session:
            session = self.Session()
        yield func(self, session, *args, **kwargs)
        if enclosed_session:
            session.commit()
            session.close()
    return decorator

class Collection:
    def __init__(self, Base, Session, ndi_class, fields):
        self.Session = Session
        table_name = class_to_collection_name(ndi_class)
        self.table =  type(table_name, (Base,), {
            '__tablename__': table_name,
            **fields
        })
        self.fields = fields
    
    def create_document(self, fields):
        return self.table(**fields)

    def create_document_from_ndi_object(self, ndi_object):
        metadata_fields = { key: getattr(ndi_object, key)
            for key in self.fields
            if key != 'flatbuffer' }
        fields = {
            'flatbuffer': ndi_object.serialize(),
            **metadata_fields
        }
        return self.create_document(fields)
    
    def extract_document_fields(self, documents):
        extract = lambda doc: { key: getattr(doc, key)
            for key in self.fields }
        if isinstance(documents, list):
            return [ extract(doc) for doc in documents ]
        else:
            return extract(documents)

    def extract_flatbuffers(self, documents):
        extract = lambda doc: getattr(doc, 'flatbuffer')
        if isinstance(documents, list):
            return [ extract(doc) for doc in documents ]
        else:
            return extract(documents)

    _sqla_filter_ops = {
        # composite types
        AndQuery: lambda conditions: and_(*conditions),
        OrQuery: lambda conditions: or_(*conditions),
        # operators
        '==': lambda field, value: field == value,
        '!=': lambda x: x,
        'contains': lambda x: x,
        'match': lambda x: x,
        '>': lambda x: x,
        '>=': lambda x: x,
        '<': lambda x: x,
        '<=': lambda x: x,
        'exists': lambda x: x,
        'in': lambda x: x,
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
            if query is not None: print(query)
            return expr if query is None else expr.filter(query)
        return filter_

    @recast_ndi_objects_to_documents
    @with_session
    def add(self, session, items):
        print(f'adding to {self.table.__tablename__}:')
        for item in items:
            id = getattr(item, 'id')
            print(f'  {id[0:7]}...', item)
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
        pass

    @with_session
    @translate_query
    def find(self, session, query=None, as_flatbuffers=True):
        filter_ = self._functionalize_query(query)
        documents = filter_(session.query(self.table)).all()
        return self.extract_flatbuffers(documents) if as_flatbuffers else self.extract_document_fields(documents)

    @recast_ndi_objects_to_documents
    @with_session
    def delete(self, session, items):
        for item in items:
            doc = session.query(self.table).get(item.id)
            session.delete(doc)
