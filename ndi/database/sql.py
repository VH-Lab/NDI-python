from __future__ import annotations
import ndi.types as T
from enum import Enum
from abc import ABCMeta
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import Table, Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy import and_, or_
from .ndi_database import NDI_Database
from functools import wraps
from ndi import NDI_Object, Experiment, DaqSystem, Probe, Epoch, Channel, Document
from ..utils import class_to_collection_name, flatten
from ..decorators import handle_iter, handle_list
from .query import Query, AndQuery, OrQuery, CompositeQuery
from .utils import check_ndi_object, listify, check_ndi_objects, update_flatbuffer, recast_ndi_objects_to_documents, translate_query, with_session, with_open_session, reduce_ndi_objects_to_ids


# =========== #
#  Constants  #
# =========== #

FLATBUFFER_KEY = 'flatbuffer'


class Datatype(Enum):
    """This enum describes the 3 types of structure a document may exist as in the :class:`SQL` database class."""
    NDI = 2
    SQL_ALCHEMY = 1
    FLATBUFFER = 0


# ============== #
#  SQL Database  #
# ============== #

class SQL(NDI_Database):
    """Interface for SQL Databases.

    .. currentmodule:: ndi.database.ndi_database

    Inherits from the :class:`NDI_Database` abstract class.

    This class aims to manage high-level database operations using the sqlalchemy (SQLA) library and serve as an interface between the NDI and SQLA systems. It maintains the SQLA engine and Session generator, directs :term:`CRUD` actions to their target :class:`Collection`\ s in the database, and is responsible for setting up, configuring, and destroying collections.

    It is closely tied to its :class:`Collection` class, which handles low-level SQLA operations like CRUD implementations. Decorators on the Collection methods are where most of the translation between NDI and SQLA objects occurs (:term:`NDI object` -> :term:`SQLA document`, :term:`NDI query` -> :term:`SQLA query`, etc.). Each :term:`NDI class` translates to a Collection instance.
    """

    _collections: T.SqlDatabaseCollections
    relationships: T.RelationshipMap = {}

    def __init__(self, connection_string: str) -> None:
        """Sets up a SQL database with collections, binds a sqlAlchemy sessionmaker, and instantiates a slqAlchemy metadata Base.

        :param connection_string: A standard SQL Server connection string.
        :type connection_string: str
        """
        self.db = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.db)
        self.Base = declarative_base()
        self.__create_collections(self.__configure_collections())

    @with_open_session
    def _sqla_open_session(self, session: T.Session) -> T.Session:
        """Exposes a session for use in a :code:`'with'` statement.
        ::
            with db._sqla_open_session() as session:
                # session operations

        This method handles session setup, commit, and close. Only for use by developers wanting to access the underlying sqlAlchemy layer.

        :param session: Recieved from decorator.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :return: A sqlAlchemy session instance.
        :rtype: Iterator[:class:`sqlalchemy.orm.session.Session`]
        """
        return session

    def execute(self, query: str):
        """Runs a `sqlAlchemy query <https://docs.sqlalchemy.org/en/13/core/connections.html>`_. Only for use by developers wanting to access the underlying sqlAlchemy layer.

        :param query: A SQL query in the format of the given database.
        :type query: str
        """
        return self.db.execute(query)

    def __configure_collections(self) -> T.Dict[T.NdiClass, T.SqlNdiCollectionConfig]:
        """Generates the configuration object for the database, not including lookup tables. Collection columns are relationships are defined here.

        :return:
        :rtype: T.SqlDatabaseConfig
        """
        return {
            Experiment: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),
                'name': Column(String),

                'daq_systems': self.define_relationship(DaqSystem, back_populates='experiment', lazy='joined', cascade='all, delete, delete-orphan'),
                'documents': self.define_relationship(Document, back_populates='experiment', lazy='joined', cascade='all, delete, delete-orphan')
            },
            DaqSystem: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),
                'name': Column(String),

                'experiment_id': Column(String, ForeignKey('experiments.id')),
                'experiment': self.define_relationship(Experiment, back_populates='daq_systems'),

                'probes': self.define_relationship(Probe, back_populates='daq_system', cascade='all, delete, delete-orphan'),
                'epochs': self.define_relationship(Epoch, back_populates='daq_system', cascade='all, delete, delete-orphan'),
                'channels': self.define_relationship(Channel, back_populates='daq_system', cascade='all, delete, delete-orphan'),
            },
            Probe: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),
                'name': Column(String),
                'reference': Column(Integer),
                'type': Column(String),

                'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
                'daq_system': self.define_relationship(DaqSystem, back_populates='probes'),

                'channels': self.define_relationship(Channel, back_populates='probe', cascade='all, delete, delete-orphan'),
            },
            Epoch: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),

                'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
                'daq_system': self.define_relationship(DaqSystem, back_populates='epochs'),

                'channels': self.define_relationship(Channel, back_populates='epoch', cascade='all, delete, delete-orphan'),
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
                'probe': self.define_relationship(Probe, back_populates='channels'),
                'epoch_id': Column(String, ForeignKey('epochs.id')),
                'epoch': self.define_relationship(Epoch, back_populates='channels'),
                'daq_system_id': Column(String, ForeignKey('daq_systems.id')),
                'daq_system': self.define_relationship(DaqSystem, back_populates='channels'),
            },
            Document: {
                'id': Column(String, primary_key=True),
                FLATBUFFER_KEY: Column(LargeBinary),
                'document_type': Column(String),
                'file_id': Column(String),
                'version_depth': Column(Integer),
                'asc_path': Column(String),

                'experiment_id': Column(String, ForeignKey('experiments.id')),
                'experiment': self.define_relationship(Experiment, back_populates='documents'),
                'parent_id': Column(String, ForeignKey('documents.id'), nullable=True),
                'parent': self.define_relationship(
                    Document,
                    after_create_collections_hook=lambda c: relationship(
                        'documents',
                        backref='children',
                        remote_side=c[Document].table.id,
                        lazy='joined',
                        join_depth=1,
                    )
                ),

                'dependencies': self.define_relationship(
                    Document,
                    after_create_collections_hook=lambda c: relationship(
                        'documents',
                        secondary=c['document_to_document'].table.__table__,
                        primaryjoin=c[Document].table.id == c['document_to_document'].table.dependant_id,
                        secondaryjoin=c[Document].table.id == c['document_to_document'].table.dependency_id,
                        backref=backref('dependants', lazy='joined'),
                        lazy='joined',
                        join_depth=1,
                    )
                )
            },
        }

    def __configure_lookup_tables(self) -> T.Dict[str, T.SqlLookupTableConfig]:
        """Generates the configuration object for database lookup tables.

        :rtype: T.SqlDatabaseConfig
        """
        return {
            'document_to_document': {
                'dependant_id': Column(String, ForeignKey('documents.id'), primary_key=True),
                'dependency_id': Column(String, ForeignKey('documents.id'), primary_key=True),
            }
        }

    def __get_columns(self, config: T.SqlNdiCollectionConfig) -> T.Dict[str, T.Column]:
        """Takes the configuration object of a single :term:`Collection` and filters it for the `sqlalchemy.Column` fields.

        :param config: 
        :type config: T.SqlNdiCollectionConfig
        :rtype: T.Dict[str, T.Column]
        """
        return {key: item for key, item in config.items() if isinstance(item, Column)}

    def __get_relationships(self, config: T.SqlNdiCollectionConfig) -> T.Dict[str, T.relationship]:
        """Takes the configuration object of a single :term:`Collection` and filters it for the `sqlalchemy.relationship` fields.

        :param config: 
        :type config: T.SqlNdiCollectionConfig
        :rtype: T.Dict[str, T.relationship]
        """
        return {
            heading: relationship_generator(self._collections)
            for heading, relationship_generator in config.items()
            if not isinstance(relationship_generator, Column)
        }

    def __create_collections(
        self,
        collection_configs: T.Dict[T.NdiClass, T.SqlNdiCollectionConfig]
    ) -> None:
        """Creates :class:`Collection`\ s from the given configs and adds them to the database.

        :param collection_configs:
        :type collection_configs: T.SqlDatabaseConfig
        """
        for ndi_class, config in collection_configs.items():
            columns = self.__get_columns(config)
            self.create_collection(ndi_class, columns, defer_create_all=True)
        for table_name, columns in self.__configure_lookup_tables().items():
            self._collections[table_name] = Collection(
                self, self.Base, self.Session, None, columns, table_name=table_name)
        self.Base.metadata.create_all(self.db)
        for ndi_class, config in collection_configs.items():
            relationships = self.__get_relationships(config)
            self.set_relationships(ndi_class, relationships)
        self.Base.metadata.create_all(self.db)

    def create_collection(
        self,
        ndi_class: T.NdiClass,
        fields: T.Dict[str, T.Column],
        defer_create_all: bool = False
    ) -> T.SqlCollection:
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
        self._collections[ndi_class] = Collection(
            self, self.Base, self.Session, ndi_class, fields)
        if not defer_create_all:
            self.Base.metadata.create_all(self.db)
        return self._collections[ndi_class]

    @handle_iter
    def drop_collection(self, ndi_class: T.NdiClass) -> None:
        """Drops collection(s) from the database.


        .. currentmodule:: ndi.ndi_object

        :param ndi_classes: One or many :term:`NDI class`\ es associated with collections(s) in the database.
        :type ndi_classes: List<:class:`NDI_Object`\ > | :class:`NDI_Object`
        """
        self._collections[ndi_class].table.__table__.drop(self.db)
        self._collections.pop(ndi_class)

    def define_relationship(
        self,
        ndi_class: T.NdiClass,
        after_create_collections_hook: T.Optional[T.Callable] = None,
        **kwargs: T.Any
    ) -> T.SqlRelationshipGenerator:
        """.. currentmodule:: ndi.database.sql

        Creates an unset :func:`sqlalchemy.orm.relationship` pointing at the given :term:`NDI class`. Set relationships with :func:`SQL.set_relationships`.

        Postponing further documentation pending NDI_Collection.

        :param ndi_class: 
        :type ndi_class: [type]
        :rtype: [type]
        """
        def create_relationship(collections: T.SqlDatabaseCollections) -> T.relationship:
            rel = after_create_collections_hook(collections) if after_create_collections_hook else relationship(
                class_to_collection_name(ndi_class), **kwargs)
            setattr(rel, '_ndi_class', ndi_class)
            return rel
        return create_relationship

    def set_relationships(
        self,
        ndi_class: T.NdiClass,
        relationships: T.Dict[str, T.relationship]
    ) -> None:
        """Sets one or many relationships on the given :term:`NDI class`.


        .. currentmodule:: ndi.database.sql

        :param ndi_class: The :term:`NDI class` associated with the :class:`Collection` the relationships are being set to.

        .. currentmodule:: ndi.ndi_object

        :type ndi_class: :class:`NDI_Object`
        :param relationships: The relationship key/value pairs, where keys resolve to backref labels and values are objects created by :func:`SQL.define_relationship`.
        :type relationships: dict
        """
        self._collections[ndi_class].set_relationships(relationships)

    def get_tables(self) -> T.Dict[T.Union[T.NdiClass, str], T.DeclarativeMeta]:
        """Gets the :term:`SQLA table`\ s in the database.

        .. currentmodule:: ndi.database.sql

        .. note::
           This bypasses the :class:`Collection` layer and is only useful for very specific operations involving the sqlalchemy layer.

        :return: NDI class keys and their :term:`SQLA table` values.
        :rtype: dict
        """
        return {ndi_class: collection.table for ndi_class, collection in self._collections.items()}

    def get_table(self, ndi_class: T.NdiClass) -> T.DeclarativeMeta:
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

    def _get_collection(self, ndi_object: T.NdiObject) -> T.SqlCollection:
        """.. currentmodule:: ndi.database.sql

        Gets the :class:`Collection` associated with the :term:`NDI class` of the given :term:`NDI object`.

        :param ndi_object:
        :type ndi_object: :term:`NDI object`
        :rtype: :class:`Collection`
        """
        return self._collections[type(ndi_object)]

    def _group_by_collection(self, ndi_objects: T.List[T.NdiObject]) -> T.Dict[T.SqlCollection, T.List[T.NdiObject]]:
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
        objects_by_collection: T.Dict[T.SqlCollection,
                                      T.List[T.NdiObject]] = {}
        for ndi_object in ndi_objects:
            Collection = self._get_collection(ndi_object)
            if Collection in objects_by_collection:
                objects_by_collection[Collection].append(ndi_object)
            else:
                objects_by_collection[Collection] = [ndi_object]
        return objects_by_collection

    @listify
    @check_ndi_objects
    def add_experiment(self, experiments: T.List[T.Experiment]) -> None:
        """.. currentmodule:: ndi.experiment

        Add one or many :class:`Experiment` instances to the database. Extracts its contents to their respective collections (ei. Probes, Channels, etc.).

        :param experiment: 
        :type experiment: List<:class:`Experiment`> | :class:`Experiment`
        """
        daq_systems = [ds for e in experiments for ds in e.daq_systems]

        def extract_dependants(ds):
            return (ds.daq_reader.get_probes(),
                    ds.daq_reader.get_epochs(),
                    ds.daq_reader.get_channels())
        grouped_dependants = zip(*map(extract_dependants, daq_systems))
        flattened_dependants = [flatten(group) for group in grouped_dependants]
        probes, epochs, channels = flattened_dependants

        # self.add([*experiments, *daq_systems, *probes, *epochs, *channels], session=session)

        self.add(experiments)
        self.add(daq_systems)
        self.add([*probes, *epochs])
        self.add(channels)

    @listify
    @check_ndi_objects
    def add(self, ndi_objects: T.List[T.NdiObject], session: T.Session = None) -> None:
        """.. currentmodule:: ndi.ndi_database

        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and adds them to the database. Objects may belong to different :term:`NDI class`\ es.

        :param ndi_object: The object(s) to be added to the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        additions_by_collection = self._group_by_collection(ndi_objects)
        for Collection, ndi_objects in additions_by_collection.items():
            Collection.add(ndi_objects, session=session)
            Collection.update_lookup_relationships(
                ndi_objects, self._collections)

    @listify
    @check_ndi_objects
    def update(self, ndi_objects: T.List[T.NdiObject]) -> None:
        """.. currentmodule:: ndi.ndi_database

        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. Objects may belong to different :term:`NDI class`\ es. 

        :param ndi_object: The object(s) to be updated in the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        updates_by_collection = self._group_by_collection(ndi_objects)
        for Collection, ndi_objects in updates_by_collection.items():
            Collection.update(ndi_objects)
            Collection.update_lookup_relationships(
                ndi_objects, self._collections)

    @listify
    @check_ndi_objects
    def upsert(self, ndi_objects: T.List[T.NdiObject]) -> None:
        """.. currentmodule:: ndi.ndi_database

        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. If an object doesn't have a document representation, it is added to the collection. Objects may belong to different :term:`NDI class`\ es. 

        :param ndi_object: The object(s) to be upserted into the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        upserts_by_collection = self._group_by_collection(ndi_objects)
        for Collection, ndi_objects in upserts_by_collection.items():
            Collection.upsert(ndi_objects)
            Collection.update_lookup_relationships(
                ndi_objects, self._collections)

    @listify
    @check_ndi_objects
    def delete(self, ndi_objects: T.List[T.NdiObject]) -> None:
        """.. currentmodule:: ndi.ndi_database

        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and deletes their :term:`document` in the database. Objects may belong to different :term:`NDI class`\ es. 

        :param ndi_object: The object(s) to be removed from the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        deletions_by_collection = self._group_by_collection(ndi_objects)
        for Collection, ndi_objects in deletions_by_collection.items():
            Collection.delete(ndi_objects)

    def find(
        self,
        ndi_class: T.NdiClass,
        query: T.Query = None,
        order_by: T.Optional[str] = None,
        as_sql_data: bool = False
    ) -> T.List[T.SqlDatabaseDatatype]:
        """Extracts all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.ndi_database`
        :param query: See :term:`NDI query`, defaults to find-all
        :type query: dict, optional
        :param order_by: Field name to order results by. Defaults to None.
        :type order_by: str, optional
        :param as_sql_data: If set to ``True``, find will return contents of SQL table row as a dict; otherwise, will return :term:`NDI object`\ s. Defaults to ``False``.
        :type as_sql_data: bool, optional
        :rtype: List<:term:`NDI object`> | dict
        """
        return self._collections[ndi_class].find(
            query=query,
            order_by=order_by,
            result_format=Datatype.SQL_ALCHEMY if as_sql_data else Datatype.NDI
        )

    def update_many(self, ndi_class: T.NdiClass, query: T.SqlaFilter = None, payload: T.SqlCollectionDocument = {}) -> None:
        """Updates all documents matching the given :term:`NDI query` in the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.ndi_database`
        :param query: See :term:`NDI query`, defaults to update-all
        :type query: dict, optional
        :param payload: Field and update values to be updated, defaults to {}
        :type payload: :term:`payload`, optional
        :param order_by: Field name to order results by. Defaults to None.
        :type order_by: str, optional
        """
        self._collections[ndi_class].update_many(
            self._collections, query=query, payload=payload)

    def delete_many(self, ndi_class: T.NdiClass, query: T.SqlaFilter = None) -> None:
        """Deletes all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`NDI_Database`
        :param query: See :term:`NDI query`, defaults to {}
        :type query: dict, optional
        """
        self._collections[ndi_class].delete_many(query=query)

    def find_by_id(self, ndi_class: T.NdiClass, id_: T.NdiId, as_sql_data: bool = False) -> T.SqlDatabaseDatatype:
        """Retrieves the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to search.
        :type ndi_class: :class:`NDI_Database`
        :param id_: The identifier of the :term:`document` to extract.
        :type id_: str
        :param as_sql_data: If set to ``True``, find will return contents of SQL table row as a dict; otherwise, will return :term:`NDI object`\ s. Defaults to ``False``.
        :type as_sql_data: bool, optional
        :rtype: :term:`NDI object`
        """
        return self._collections[ndi_class].find_by_id(
            id_,
            result_format=Datatype.SQL_ALCHEMY if as_sql_data else Datatype.NDI
        )

    def update_by_id(self, ndi_class: T.NdiClass, id_: T.NdiId, payload: T.SqlCollectionDocument = {}) -> None:
        """Updates the :term:`NDI object` with the given id from the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to update.
        :type ndi_class: :class:`NDI_Database`
        :param id_: The identifier of the :term:`document` to update.
        :type id_: str
        :param payload: Field and update values to be updated, defaults to {}
        :type payload: :term:`payload`, optional
        """
        self._collections[ndi_class].update_by_id(
            id_, payload=payload)

    def delete_by_id(self, ndi_class: T.NdiClass, id_: T.NdiId) -> None:
        """Deletes the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`NDI_Database`
        :param id_: The identifier of the :term:`document` to delete.
        :type id_: str
        """
        self._collections[ndi_class].delete_by_id(id_)


# ============ #
#  Collection  #
# ============ #

class Collection:
    """.. ndi.database.sql

    Collection class for :class:`SQL` database. :term:`CRUD` operations on this collection are passed on to is corresponding table in the database.

    This class and its associated decorators attempt to encapsulate as much of the sqlalchemy logic as possible (not including database level systems like the Session and engine objects).

    Decorators on the Collection methods are where most of the translation between NDI and SQLA objects occurs (:term:`NDI object` -> :term:`SQLA document`, :term:`NDI query` -> :term:`SQLA query`, etc.). 

    Each Collection instance must have a corresponding :term:`NDI class`.
    """

    def __init__(
        self,
        db: T.Engine,
        Base: T.DeclarativeMeta,
        Session: T.Session,
        ndi_class: T.Union[T.NdiClass, str, None],
        fields: T.Dict[str, T.Column],
        table_name: T.Optional[str] = None
    ) -> None:
        """Initializes a :class:`SQL` :class:`Collection`.

        :param Base: `SQLA Metadata Base <https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/api.html#api-reference>`_
        :type Base: :class:`sqlalchemy.ext.declarative.api.DeclarativeMeta`
        :param Session: `SQLA Session <https://docs.sqlalchemy.org/en/13/orm/session.html>`_
        :type Session: :class:`sqlalchemy.orm.session.sessionmaker`
        :param ndi_class: The associated :term:`NDI class`. If table_name is defined, this will be set to None.

        .. currentmodule:: ndi.ndi_object

        :type ndi_class: :class:`NDI_Object`
        :param fields: 
        :type fields:
        :param table_name: Lookup tables do not have an :term:`NDI class`, so their name must be explicitly defined. Defaults to None.
        :type table_name: str, optional
        """
        self.db = db
        self.Session = Session
        self.ndi_class = None if table_name else ndi_class
        self.table_name = class_to_collection_name(ndi_class) if isinstance(
            ndi_class, ABCMeta) else table_name or str(ndi_class)
        print(table_name)
        self.table: T.DeclarativeMeta = type(self.table_name, (Base,), {
            '__tablename__': self.table_name,
            **fields
        })
        self.fields = fields
        self.relationships: T.List[T.SqlRelationship] = []

    def lookup_relationships(self) -> T.List[T.SqlRelationship]:
        """Filter relationships for those relying on a secondary(lookup) table.
        
        :rtype: T.List[T.SqlRelationship]
        """
        return [r for r in self.relationships if r.relationship.secondary is not None]

    def __for_self_referencing_relationships_too(self, relationship: T.SqlRelationship, cb: T.Callable[[str], T.Any]) -> None:
        """Checks to see if the given relationship is self-referencing. If false, calls the given function once with the relationship's reference key. If true, calls the given function twice, once with each key.

        For example, given a table `people`, where each person may have either a child or parent relationship with another person, there would only be one self-referencing relationship configured. If we want to operate on both relations we could call this method on that single relationship and have both `child` and `parent` fields affected.

        ::
            # a common pattern:
            def run(relationship_key):
                ...some operations...
            for r in many_relationships:
                __for_self_referencing_relationships_too(r, run)
        
        .. currentmodule:: ndi.database.sql

        :param relationship:
        :type relationship: :class:`Relationship`
        :param cb: The function to call 
        :type cb: function
        """
        cb(relationship.key)
        if hasattr(relationship.relationship, '_is_self_referential') and relationship.relationship._is_self_referential:
            if backref_key := relationship.relationship.back_populates:
                cb(backref_key)

    def set_relationships(self, relationships: T.Dict[str, T.relationship]) -> None:
        """Set the collection's relationships to its :term:`SQLA table`.

        :param relationships: The relationship key/value pairs, where keys resolve to backref labels and values are objects created by :func:`SQL.define_relationship`.
        :type relationships: dict
        """
        for key, relation in relationships.items():
            setattr(self.table, key, relation)
            self.relationships.append(Relationship(
                target_collection=relation._ndi_class,
                key=key,
                sqla_relationship=relation,
            ))

    @with_session
    def update_lookup_relationships(
        self,
        session: T.Session,
        ndi_objects: T.List[T.NdiObject],
        db_collections: T.SqlDatabaseCollections
    ) -> None:
        """Updates the relationships of the five ndi_objects for each many-to-many relationship associated with this collection.
        
        :param session:
        :type session: T.Session
        :param ndi_objects:
        :type ndi_objects: T.List[T.NdiObject]
        :param db_collections:
        :type db_collections: T.SqlDatabaseCollections
        """
        for r in self.lookup_relationships():
            for ndi_object in ndi_objects:
                doc = session.query(self.table).get(ndi_object.id)

                def run(r_key):
                    if hasattr(ndi_object, r_key):
                        relation_ids = getattr(ndi_object, r_key)
                        self._update_lookup_relationships(
                            r, doc, relation_ids, db_collections, session)
                self.__for_self_referencing_relationships_too(r, run)

    def _update_lookup_relationships(
        self,
        relationship: T.SqlRelationship,
        document: T.SqlaDocument,
        relation_ids: T.List[str],
        db_collections: T.SqlDatabaseCollections,
        session: T.Session
    ) -> None:
        """Given a self-referencing many-to-many relatonship, a document, and the ids of that document's relations, updates the relationship's lookup table with all new relationships.
        
        :param relationship:
        :type relationship: T.SqlRelationship
        :param document:
        :type document: T.SqlaDocument
        :param relation_ids:
        :type relation_ids: T.List[str]
        :param db_collections:
        :type db_collections: T.SqlDatabaseCollections
        :param session:
        :type session: T.Session
        """
        # clear all old relationships
        setattr(document, relationship.key, [])

        # add all incoming relationships
        target_table = db_collections[relationship.relationship._ndi_class].table
        relation_docs = session.query(target_table).filter(
            target_table.id.in_(relation_ids)).all()
        for relation_doc in relation_docs:
            getattr(document, relationship.key).append(relation_doc)

    def create_document(self, fields: T.Dict[str, T.Column]) -> T.SqlaDocument:
        """Create a :term:`SQLA document` with its respective fields/values

        .. currentmodule:: ndi.database.sql

        :param fields: Contains key:value pairs representing the documents table values per column.
        :type fields: dict
        :return: A :term:`SQLA document`.
        :rtype: :class:`sqlalchemy.ext.declarative.api.DeclarativeMeta`
        """
        return self.table(**fields)

    def create_document_from_ndi_object(self, ndi_object: T.NdiObject) -> T.SqlaDocument:
        """Converts an :term:`NDI object` to a :term:`SQLA document`.

        :param ndi_object:
        :type ndi_object: :term:`NDI class`
        :return: A :term:`SQLA document`.
        :rtype: :class:`sqlalchemy.ext.declarative.api.DeclarativeMeta`
        """
        metadata_fields = {
            key: getattr(ndi_object, key)
            for key in self.fields
            if key != FLATBUFFER_KEY
        }
        def reduce_to_ids(objects): 
            return [obj.id for obj in objects] if isinstance(objects, list) else objects.id
        def run(r_key):
            if r_key in metadata_fields:
                metadata_fields[r_key] = reduce_to_ids(
                    getattr(ndi_object, r_key))
        for r in self.relationships:
            self.__for_self_referencing_relationships_too(r, run)
        fields = {
            FLATBUFFER_KEY: ndi_object.serialize(),
            **metadata_fields,
        }
        return self.create_document(fields)

    @handle_list
    def normalize_documents(
        self,
        document: T.SqlaDocument
    ) -> T.SqlCollectionDocument:
        """Convert one or many :term:`SQLA document`\ s into ``dict``s.

        :param document: Documents as they are recieved from SQLA database operations.
        :type document: List<:term:`SQLA document`> | :term:`SQLA document`
        :return: Documents simplified to ``dict``s, with only Columns/values kept.
        :rtype: List<dict> | dict
        """
        fields = {
            key: getattr(document, key)
            for key in self.fields
        }
        def run(r_key):
            relations = getattr(document, r_key)
            if relations:
                fields[r_key] = [document.id for document in relations]\
                    if isinstance(relations, list)\
                    else relations.id
        for r in self.relationships:
            self.__for_self_referencing_relationships_too(r, run)
        return fields

    @handle_list
    def extract_flatbuffers(self, document: T.SqlaDocument) -> bytearray:
        """Extract the flatbuffer(s) of one or many :term:`SQLA document`\ s.

        :param document: Documents as they are recieved from SQLA database operations.
        :type document:  List<:term:`SQLA document`> | :term:`SQLA document`
        :return: Document's flatbuffer serialization.
        :rtype: List<bytearray> | bytearray
        """
        return getattr(document, FLATBUFFER_KEY)

    @handle_list
    def ndi_objects_from_documents(self, document: T.SqlaDocument) -> T.NdiObject:
        """Creates :term:`NDI object`\ s from documents and rehydrates relationships defined in secondary (lookup) tables.
        
        :param document: 
        :type document: T.SqlaDocument
        :raises TypeError: Thrown when called on a lookup-table collection.
        :rtype: T.NdiObject
        """
        flatbuffer = self.extract_flatbuffers(document)
        if not self.ndi_class or isinstance(self.ndi_class, str):
            raise TypeError(
                'This method may only be used on a collection with an associated NDI class. Lookup tables do not have NDI object equivalents.')
        if isinstance(flatbuffer, bytearray):
            pass
        elif isinstance(flatbuffer, bytes):
            flatbuffer = bytearray(flatbuffer)
        else:
            raise TypeError(f'Unexpected type {type(flatbuffer)} for field {FLATBUFFER_KEY}. Expected bytearray.')
        ndi_object = self.ndi_class.from_flatbuffer(flatbuffer)
        def run(r_key):
            if hasattr(ndi_object, r_key):
                relations = getattr(document, r_key)
                relation_ids = [doc.id for doc in relations] if isinstance(
                    relations, list) else relations.id
                setattr(ndi_object, r_key, relation_ids)
        for r in self.relationships:
            self.__for_self_referencing_relationships_too(r, run)
        return ndi_object

    def __formatted_results(self, documents: T.SqlaDocument, result_format: T.DatatypeEnum) -> T.OneOrManySqlDatabaseDatatype:
        """Formats the given documents as either :term:`NDI object`\ s, :term:`SQLA document`\ s, or :term:`flatbuffer`\ s.
        
        .. currentmodule:: ndi.database.sql

        :param documents: 
        :type documents: T.SqlaDocument
        :param result_format: 
        :type result_format: Datatype
        :rtype: T.OneOrManySqlDatabaseDatatype
        """
        if result_format is Datatype.SQL_ALCHEMY:
            return self.normalize_documents(documents)
        elif result_format is Datatype.FLATBUFFER:
            return self.extract_flatbuffers(documents)
        else:
            return self.ndi_objects_from_documents(documents)

    _sqla_filter_ops: T.SqlFilterMap = {
        # composite types
        AndQuery: lambda conditions: and_(*conditions),
        OrQuery: lambda conditions: or_(*conditions),
        # operators
        '==': lambda field, value: field == value,
        '!=': lambda field, value: field != value,
        'contains': lambda field, value: field.contains(value),
        'match': lambda field, value: field.match(value),
        '>': lambda field, value: field > value,
        '>=': lambda field, value: field >= value,
        '<': lambda field, value: field < value,
        '<=': lambda field, value: field <= value,
        'exists': lambda field, value: field,
        'in': lambda field, value: field.in_(value),
    }

    def generate_sqla_filter(self, query: T.Query) -> T.Callable[[T.Query], T.SqlaFilter]:
        """Convert an :term:`NDI query` to a :term:`SQLA query`.

        :param query:
        :type query: :term:`NDI query`
        :return:
        :rtype: :term:`SQLA query`
        """
        def recurse(q: T.Query) -> T.SqlaFilter:
            if isinstance(q, CompositeQuery):
                nested_queries = [recurse(nested_q) for nested_q in q]
                return self._sqla_filter_ops[type(q)](nested_queries)
            else:
                field, operator, value = q.query
                column = self.fields[field]
                return self._sqla_filter_ops[operator](column, value)
        return recurse(query)

    def _functionalize_query(self, query: T.SqlaFilter) -> T.Callable[[T.SqlaQuery], T.SqlaQuery]:
        """This function allows us to conditionally set a filter operation on a :term:`SQLA session query`. This allows us to interpret the absence of an :term:`NDI query` or :term:`SQLA query` as being equivalent to ``SELECT *`` within the queried table.

        :param query:
        :type query: :term:`SQLA query` | None
        :return: A :term:`SQLA session query`.
        :rtype: sqlalchemy.orm.query.Query
        """
        def filter_(expr: T.SqlaQuery) -> T.SqlaQuery:
            return expr if query is None else expr.filter(query)
        return filter_

    @recast_ndi_objects_to_documents
    @with_session
    def add(self, session: T.Session, items: T.List[T.SqlaDocument]) -> None:
        """Adds :term:`NDI object`\ s to the :class:`Collection` as :term:`SQLA document`\ s.

        .. currentmodule: ndi.database

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param items: Argument is passed in as :term:`NDI object`\ s and is converted to :term:`SQLA document`\ s by :func:`utils.recast_ndi_objects_to_documents`.
        :type items: List<:term:`SQLA document`>
        """
        session.add_all(items)

    @recast_ndi_objects_to_documents
    @with_session
    def update(self, session: T.Session, items: T.List[T.SqlaDocument]) -> None:
        """Updates (replaces) the :term:`document`\ s of the given :term:`NDI object`\ s in the :class:`Collection` based on the object's id.

        .. currentmodule: ndi.database

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param items: Argument is passed in as :term:`NDI object`\ s and is converted to :term:`SQLA document`\ s by :func:`utils.recast_ndi_objects_to_documents`.
        :type items: List<:term:`SQLA document`>
        """
        q = session.query(self.table)
        for item in items:
            doc = q.get(item.id)
            for key in self.fields:
                setattr(doc, key, getattr(item, key))

    @recast_ndi_objects_to_documents
    @with_session
    def upsert(self, session: T.Session, items: T.List[T.SqlaDocument]) -> None:
        """Updates (replaces) the :term:`document`\ s of the given :term:`NDI object`\ s in the :class:`Collection`. Objects that do not already exist are added.

        .. currentmodule: ndi.database

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param items: Argument is passed in as :term:`NDI object`\ s and is converted to :term:`SQLA document`\ s by :func:`utils.recast_ndi_objects_to_documents`.
        :type items: List<:term:`SQLA document`>
        """
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
    def delete(self, session: T.Session, items: T.List[T.SqlaDocument]) -> None:
        """Removes the :term:`document`\ s of the given :term:`NDI object`\ s from the :class:`Collection`.

        .. currentmodule: ndi.database

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param items: Argument is passed in as :term:`NDI object`\ s and is converted to :term:`SQLA document`\ s by :func:`utils.recast_ndi_objects_to_documents`.
        :type items: List<:term:`SQLA document`>
        """
        for item in items:
            doc = session.query(self.table).get(item.id)
            session.delete(doc)

    @with_session
    @translate_query
    def find(self, session: T.Session, query: T.SqlaFilter = None, order_by: T.Optional[str] = None, result_format: T.DatatypeEnum = Datatype.NDI) -> T.List[T.SqlDatabaseDatatype]:
        """.. currentmodule:: ndi.database.sql

        Extracts the :term:`document`\ s in the :class:`Collection` matching the given :term:`SQLA query`.

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param query: See :term:`SQLA query`. Defaults to find-all.
        :type query: :class:`sqlalchemy.orm.query.Query`, optional
        :param order_by: :term:`label`. Defaults to last-updated.
        :type order_by: str, optional
        :param as_flatbuffers: If False, find will return the results as :term:`SQLA document`\ s as ``dict``s; otherwise, will return :term:`flatbuffers`\ s as ``bytearray``s. Defaults to True.
        :type as_flatbuffers: bool, optional
        :rtype: List<bytearray> | List<dict>
        """
        filter_ = self._functionalize_query(query)
        documents = filter_(session.query(self.table)).order_by(order_by).all()
        formatted_results = self.__formatted_results(documents, result_format)
        if isinstance(formatted_results, list):
            return formatted_results
        else:
            raise RuntimeError('Unexpected return value from sqlachemy library. If this occurs, it is likely that the library api has changed since the last update.')

    @with_session
    @translate_query
    def delete_many(self, session: T.Session, query: T.SqlaFilter = None) -> None:
        """Deletes the :term:`document`\ s in the :class:`Collection` matching the given :term:`SQLA query`.

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param query: See :term:`SQLA query`. Defaults to find-all.
        :type query: :class:`sqlalchemy.orm.query.Query`, optional
        """
        filter_ = self._functionalize_query(query)
        documents = filter_(session.query(self.table)).all()
        for doc in documents:
            session.delete(doc)

    @with_session
    def find_by_id(self, session: T.Session, id_: T.NdiId, result_format: T.DatatypeEnum = Datatype.NDI) -> T.SqlDatabaseDatatype:
        """Extracts the :term:`document` in the :class:`Collection` matching the given id.

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param id_: See :term:`NDI ID`.
        :type id_: str
        :param as_flatbuffers: If False, find will return the results as :term:`SQLA document`\ s as ``dict``s; otherwise, will return :term:`flatbuffers`\ s as ``bytearray``s. Defaults to True.
        :type as_flatbuffers: bool, optional
        :rtype: bytearray | dict
        """
        document = session.query(self.table).get(id_)
        formatted_results = self.__formatted_results(document, result_format)
        if not isinstance(formatted_results, list):
            return formatted_results
        else:
            raise RuntimeError('Unexpected return value from sqlachemy library. If this occurs, it is likely that the library api has changed since the last update.')

    @with_session
    def update_by_id(self, session: T.Session, id_: T.NdiId, payload: T.SqlCollectionDocument = {}) -> None:
        """Updates the :term:`document` in the :class:`Collection` matching the given id with payload and returns the updated document flatbuffer.

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param id_: See :term:`NDI ID`.
        :type id_: str
        :param payload: See :term:`payload`.
        :type payload: dict
        :rtype: bytearray
        """
        document = session.query(self.table).get(id_)
        self.__update_sqla_partial_document(document, payload)

    @with_session
    def delete_by_id(self, session: T.Session, id_: T.NdiId) -> None:
        """Deletes the :term:`document` in the :class:`Collection` matching the given id.

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param id_: See :term:`NDI ID`.
        :type id_: str
        """
        document = session.query(self.table).get(id_)
        session.delete(document)

    @with_session
    @translate_query
    def update_many(self, session: T.Session, db_collections: T.SqlDatabaseCollections, query: T.SqlaFilter = {}, payload: T.SqlCollectionDocument = {}) -> None:
        """Updates (replaces) the :term:`document`\ s of the given :term:`NDI object`\ s in the :class:`Collection` matching the given :term:`SQLA query`.

        :param session: See :term:`SQLA session`. Argument passed by :func:`utils.with_session`.
        :type session: :class:`sqlalchemy.orm.session.Session`
        :param query: See :term:`SQLA query`. Defaults to find-all.
        :type query: :class:`sqlalchemy.orm.query.Query`, optional
        :param payload: See :term:`payload`.
        :type payload: dict
        :param order_by: :term:`label`. Defaults to last-updated.
        :type order_by: str, optional
        :rtype: List<bytearray>
        """
        filter_ = self._functionalize_query(query)
        documents = filter_(session.query(self.table)).all()
        for d in documents:
            # handle and remove many-to-many relationship items in payload
            for r in self.lookup_relationships():
                updated_relation_ids = payload[r.key]
                del payload[r.key]
                if updated_relation_ids and isinstance(updated_relation_ids, list):
                    updated_relation_id_strings = [str(id_) for id_ in updated_relation_ids]
                    self._update_lookup_relationships(
                        r, d, updated_relation_id_strings, db_collections, session)
            self.__update_sqla_partial_document(d, payload)

    def __update_sqla_partial_document(self, document: T.SqlaDocument, payload: T.SqlCollectionDocument) -> None:
        """Modifies a document in place with the key:value pairs in the given payload.

        :param document:
        :type document: :term:`SQLA document`
        :param payload: See :term:`payload`.
        :type payload: dict
        """
        for key, value in payload.items():
            setattr(document, key, value)
        if hasattr(document, FLATBUFFER_KEY):
            self.__update_sqla_flatbuffer(document, payload)

    def __update_sqla_flatbuffer(self, document: T.SqlaDocument, payload: T.SqlCollectionDocument) -> None:
        """Modifies the flatbuffer of a document with the key:value pairs in the given payload.
        
        :param document: [description]
        :type document: T.SqlaDocument
        :param payload: [description]
        :type payload: T.SqlCollectionDocument
        """
        old_flatbuffer = getattr(document, FLATBUFFER_KEY)
        updated_flatbuffer = update_flatbuffer(
            self.ndi_class, old_flatbuffer, payload)
        setattr(document, FLATBUFFER_KEY, updated_flatbuffer)


class Relationship:
    """This class wraps the :class:`sqlalchemy.relationship` class with ndi-specific attributes. These relationships are tied to their key in a collection, and are used to establish the relationship between that collection and another one.    
    """
    def __init__(self, target_collection: T.SqlCollectionName, key: str, sqla_relationship: T.relationship) -> None:
        """Initializes an NDI relationship.
        
        :param target_collection: The other collection in the relationship.
        :type target_collection: T.SqlCollectionName
        :param key: The key of the field in the 
        :type key: str
        :param sqla_relationship: [description]
        :type sqla_relationship: T.relationship
        """
        self.relationship = sqla_relationship
        self.reverse_relationship = self.__get_reverse_relationship()
        self.key = key
        self.secondary_key = self.__get_secondary_key()
        self.collection = target_collection

    def __get_reverse_relationship(self) -> T.Union[T.relationship, None]:
        """For each relationship defined there may be a reverse relationship created by sqlalchemy. This method extracts that relationship object if it exists.
        
        :rtype: T.Union[T.relationship, None]
        """
        try:
            return next(iter(self.relationship._reverse_property))
        except StopIteration:
            return None

    def __get_secondary_key(self) -> T.Union[str, None]:
        """For bi-directional self-referential relationships there is a secondary key. If it exists, this method extracts it.
        
        :return: [description]
        :rtype: T.Union[str, None]
        """
        if self.relationship._is_self_referential and self.relationship.back_populates:
            return self.relationship.back_populates
        else:
            return None
