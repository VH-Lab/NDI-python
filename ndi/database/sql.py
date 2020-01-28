from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import String, LargeBinary, Integer
from sqlalchemy.orm import sessionmaker
from .base_db import BaseDB
from contextlib import contextmanager
from ndi import Experiment, DaqSystem, Probe, Epoch, Channel
from ndi.utils import class_to_collection_name

def with_session(func):
    """Handle session instantiation, commit, and close operations for a class method."""
    def decorator(self, *args, **kwargs):
        session = self.Session()
        output = func(self, session, *args, **kwargs)
        session.commit()
        session.close()
        return output
    return decorator

def with_open_session(func):
    """Handle session setup/teardown as a context manager for a class method."""
    @contextmanager
    def decorator(self, *args, **kwargs):
        session = self.Session()
        yield func(self, session, *args, **kwargs)
        session.commit()
        session.close()
    return decorator


class SQL(BaseDB):
    """Interface for SQL Databases.
    Adheres to standard methods in BaseDB Abstract Class."""
    def __init__(self, connection_string):
        """Sets up a SQL database with collections and binds a sqlAlchemy sessionmaker.
        
        :param connection_string: A standard SQL Server connection string.
        :type connection_string: str
        """
        self.db = create_engine(connection_string)
        self.Base = declarative_base()
        self.Session = sessionmaker(bind=self.db)
        self.__create_collections()

    def execute(self, query):
        """Runs a custom sql query.
        
        :param query: A SQL query in the format of the given database.
        :type query: str
        """
        self.db.execute(query)

    def add_experiment(self, experiment):
        """Add an NDI Experiment Object to the database.
        
        :param experiment: NDI Experiment Object
        :type experiment: :class:`ndi.Experiment`
        """
        return 

    def __create_collections(self):
        """Create Base Collections described in :class:`ndi.database.BaseDB`."""
        collections_columns = {
            Experiment: {
                'flat_buffer': Column(LargeBinary)
            },
            DaqSystem: {
                'experiment_id': Column(Integer, ForeignKey('experiments.id')),
                'flat_buffer': Column(LargeBinary)
            },
            Probe: {
                'daq_system_id': Column(Integer, ForeignKey('daq_systems.id')),
                'flat_buffer': Column(LargeBinary)
            },
            Epoch: {
                'daq_system_id': Column(Integer, ForeignKey('daq_systems.id')),
                'flat_buffer': Column(LargeBinary)
            },
            Channel: {
                'probe_id': Column(Integer, ForeignKey('probes.id')),
                'flat_buffer': Column(LargeBinary)
            }
        }
        for collection, columns in collections_columns.items():
            self.create_collection(collection, **columns)
        print(self._collections)
        print(self.Base)
        print(self.Base.metadata.tables)

    def create_collection(self, ndi_class, **fields):
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
        table_name = class_to_collection_name(ndi_class)
        self._collections[ndi_class] = Table(self.Base, table_name, **fields)
        return self._collections[ndi_class]

    def get_tables(self):
        return self.Base.metadata.sorted_tables


    def add(self, ndi_object):
        pass

    def find(self, ndi_class, **query):
        pass
    
    def find_by_id(self, ndi_class, id_):
        pass

    def update(self):
        # params tbd
        pass
    
    def update_by_id(self, ndi_class, id, payload):
        pass

    def upsert(self, ndi_objects):
        pass

    def delete(self, ndi_entity, **query):
        pass
    
    def delete_by_id(self, ndi_class, id_):
        pass



class Table:
    def __init__(self, Base, table_name, **fields):
        self.metadata = type(table_name, (Base,), {
            '__tablename__': table_name,
            'id': Column(Integer, primary_key=True),
            **fields
        })
        
    def find(self, session, Table, **kwargs):
        results = session.query(Table).filter_by(**kwargs).all()
        return results

    def find_by_id(self, session, Table, id):
        results = session.query(Table).get(id)
        return results

    def add(self, session, payload):
        if type(payload) is list:
            for item in payload:
                session.add(item)
        else:
            return session.add(payload)

    def upsert(self, session, Table, filters, payload):
        results = session.query(Table).filter_by(**filters)
        if len(results.all()) == 0:
            self.add(Table(**payload))
        else:
            results.update(payload, synchronize_session='evaluate')

    def upsert_by_id(self, session, Table, id, payload):
        results = session.query(Table).get(id)
        if len(results.all()) == 0:
            self.add(Table(**payload))
        else:
            results.update(payload, synchronize_session='evaluate')

    def update(self, session, Table, filters, payload):
        return session.query(Table).filter_by(**filters).update(payload, synchronize_session='evaluate')

    def update_by_id(self, session, Table, id, payload):
        return session.query(Table).get(id).update(payload, synchronize_session='evaluate')

    def delete(self, session, Table, **kwargs):
        results = session.query(Table).filter_by(**kwargs).all()
        for instance in results:
            session.delete(instance)

    def delete_by_id(self, session, Table, id):
        instance = session.query(Table).get(id)
        session.delete(instance)

    def delete_all(self, session, Table):
        session.query(Table).delete()




# class SQL(BaseDB):
#     def __init__(self, connection_string):
#         self.db = create_engine(connection_string)
#         self.tables = {}
#         self.create_collections()
#         self.Session = sessionmaker(bind=self.db)

#     def execute(self, query):
#         self.db.execute(query)

#     def add_experiment(self):
#         return 

#     def create_collections(self):
#         self.create_table('experiments', {
#             'flat_buffer': Column(LargeBinary)
#         })
#         self.create_table('daq_systems', {
#             'experiment_id': Column(Integer, ForeignKey('experiments.id')),
#             'flat_buffer': Column(LargeBinary)
#         })
#         self.create_table('epochs', {
#             'daq_system_id': Column(Integer, ForeignKey('daq_systems.id')),
#             'flat_buffer': Column(LargeBinary)
#         })
#         self.create_table('probes', {
#             'daq_system_id': Column(Integer, ForeignKey('daq_systems.id')),
#             'flat_buffer': Column(LargeBinary)
#         })
#         self.create_table('channels', {
#             'probe_id': Column(Integer, ForeignKey('probes.id')),
#             'flat_buffer': Column(LargeBinary)
#         })
    
#     def create_table(self, table_name, columns):
#         self.tables[table_name] = type(table_name, (Base,), {
#             '__tablename__': table_name,
#             'id': Column(Integer, primary_key=True),
#             **columns
#         })
#         Base.metadata.create_all(self.db)
#         return self.tables[table_name]

#     def get_tables(self):
#         return Base.metadata.sorted_tables

#     @with_open_session
#     def find(self, session, Table, **kwargs):
#         results = session.query(Table).filter_by(**kwargs).all()
#         return results

#     @with_open_session
#     def find_by_id(self, session, Table, id):
#         results = session.query(Table).get(id)
#         return results

#     @with_session
#     def add(self, session, payload):
#         if type(payload) is list:
#             for item in payload:
#                 session.add(item)
#         else:
#             return session.add(payload)

#     @with_session
#     def upsert(self, session, Table, filters, payload):
#         results = session.query(Table).filter_by(**filters)
#         if len(results.all()) == 0:
#             self.add(Table(**payload))
#         else:
#             results.update(payload, synchronize_session='evaluate')

#     @with_session
#     def upsert_by_id(self, session, Table, id, payload):
#         results = session.query(Table).get(id)
#         if len(results.all()) == 0:
#             self.add(Table(**payload))
#         else:
#             results.update(payload, synchronize_session='evaluate')

#     @with_session
#     def update(self, session, Table, filters, payload):
#         return session.query(Table).filter_by(**filters).update(payload, synchronize_session='evaluate')

#     @with_session
#     def update_by_id(self, session, Table, id, payload):
#         return session.query(Table).get(id).update(payload, synchronize_session='evaluate')

#     @with_session
#     def delete(self, session, Table, **kwargs):
#         results = session.query(Table).filter_by(**kwargs).all()
#         for instance in results:
#             session.delete(instance)

#     @with_session
#     def delete_by_id(self, session, Table, id):
#         instance = session.query(Table).get(id)
#         session.delete(instance)

#     @with_session
#     def delete_all(self, session, Table):
#         session.query(Table).delete()
        
