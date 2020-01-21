from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import sessionmaker
from .base_db import BaseDB
from .types import String, Blob, Integer
from contextlib import contextmanager

Base = declarative_base()

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
    def __init__(self, connection_string):
        self.db = create_engine(connection_string)
        self.tables = {}
        self.Session = sessionmaker(bind=self.db)

    def execute(self, query):
        self.db.execute(query)

    def add_experiment(self):
        return 

    def create_collections(self):
        self.create_table('experiments', {
            'flat_buffer': Blob()
        })
        self.create_table('daq_systems', {
            'experiment_id': Integer(ForeignKey('experiments.id')),
            'flat_buffer': Blob()
        })
        self.create_table('epochs', {
            'daq_system_id': Integer(ForeignKey('daq_systems.id')),
            'flat_buffer': Blob()
        })
        self.create_table('probes', {
            'daq_system_id': Integer(ForeignKey('daq_systems.id')),
            'flat_buffer': Blob()
        })
        self.create_table('channels', {
            'probe_id': Integer(ForeignKey('probes.id')),
            'flat_buffer': Blob()
        })
    
    def create_table(self, table_name, columns):
        self.tables[table_name] = type(table_name, (Base,), {
            '__tablename__': table_name,
            'id': Integer(primary_key=True),
            **columns
        })
        Base.metadata.create_all(self.db)
        return self.tables[table_name]

    def get_tables(self):
        return Base.metadata.sorted_tables

    @with_open_session
    def find(self, session, Table, **kwargs):
        results = session.query(Table).filter_by(**kwargs).all()
        return results

    @with_session
    def add(self, session, payload):
        if type(payload) is list:
            for item in payload:
                session.add(item)
        else:
            return session.add(payload)

    @with_session
    def upsert(self, session, Table, filters, payload):
        results = session.query(Table).filter_by(**filters)
        if len(results.all()) == 0:
            self.add(Table(**payload))
        else:
            results.update(payload, synchronize_session='evaluate')

    @with_session
    def update(self, session, Table, filters, payload):
        return session.query(Table).filter_by(**filters).update(payload, synchronize_session='evaluate')

    @with_session
    def delete(self, session, Table, **kwargs):
        results = session.query(Table).filter_by(**kwargs).all()
        for instance in results:
            session.delete(instance)

    @with_session
    def delete_all(self, session, Table):
        session.query(Table).delete()
        
