from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import sessionmaker
from .base_db import BaseDB
from .types import String, Blob, Integer

Base = declarative_base()

class SQL(BaseDB):
    def __init__(self, connection_string):
        self.db = create_engine(connection_string, echo=True)
        self.tables = {}
        self.Session = sessionmaker(bind=self.db)

    def execute(self, query):
        self.db.execute(query)

    def add_experiment(self):
        return 

    def create_collections(self):
        self.create_table('experiments', {
            'flatBuffer': Blob()
        })
        self.create_table('daq_systems', {
            'experiment_id': String(ForeignKey('experiments.id')),
            'flatBuffer': Blob()
        })
        self.create_table('epochs', {
            'daq_system_id': String(ForeignKey('daq_systems.id')),
            'flatBuffer': Blob()
        })
        self.create_table('probes', {
            'daq_system_id': String(ForeignKey('daq_systems.id')),
            'flatBuffer': Blob()
        })
        self.create_table('channels', {
            'probe_id': String(ForeignKey('probes.id')),
            'flatBuffer': Blob()
        })
    
    def create_table(self, table_name, columns):
        self.tables[table_name] = type(table_name, (Base,), {
            '__tablename__': table_name,
            'id': String(primary_key=True),
            **columns
        })
        Base.metadata.create_all(self.db)
        return self.tables[table_name]

    def __finish_session(self, session):
        session.commit()
        session.close()

    def add(self, item):
        session = self.Session()
        session.add(item)
        self.__finish_session(session)

    def find(self, Table, **kwargs):
        session = self.Session()
        result = session.query(Table).filter_by(**kwargs).all()
        return result
