from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object
from .document import Document
from .epoch import Epoch
from .probe import Probe
from .channel import Channel
from .query import Query as Q
from uuid import uuid4
from .constants import EXPERIMENT_DOCUMENT_TYPE


class Experiment(NDI_Object):
    """
    A flatbuffer interface for experiments.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    DOCUMENT_TYPE = EXPERIMENT_DOCUMENT_TYPE

    def __init__(self, name: str, daq_system_ids: T.List[T.DaqSystem] = [], id_: T.NdiId = None):
        """Experiment constructor: initializes with fields defined in `ndi_schema <https://>`_'s Experiment table. For use when creating a new Experiment instance from scratch.
        ::
            new_experiment = Experiment(**fields)

        .. currentmodule:: ndi.daq_system

        :param name: [description]
        :type name: str
        :param daq_system_ids: a list of daq_system instances, defaults to []
        :type daq_system_ids: List[:class:`DaqSystem`], optional
        :param id_: = defaults to None
        :type id_: str, optional
        """
        super().__init__(id_)
        self.metadata['name'] = name
        self.metadata['type'] = self.DOCUMENT_TYPE
        self.metadata['experiment_id'] = self.id
        self.add_data_property('daq_system_ids', [])
        for daq_system in daq_system_ids:
            self.add_daq_system(daq_system)
    
    def __overwrite_with_document(self, document):
        self.document = document

    def connect(self, database=None, binary_collection=None, load_existing=False):
        """This will connect the experiment to the database and binary collection. 
        If this experiment already exists in the database (identified by _metadata.name),
        then this experiment is loaded with its contents in database.
        Otherwise, this experiment is added to the database a new experiment.

        :param database: [description], defaults to None
        :type database: [type], optional
        :param binary_collection: [description], defaults to None
        :type binary_collection: [type], optional
        :param load_existing: [description], defaults to False
        :type load_existing: bool, optional
        :raises RuntimeError: [description]
        :raises Warning: [description]
        :return: [description]
        :rtype: [type]
        """
        if database: 
            self.ctx = database
            isExperiment = Q('_metadata.type') == self.DOCUMENT_TYPE
            ownName = self.metadata['name']
            hasOwnName = Q('_metadata.name') == ownName
            preexisting_experiment = database.find(isExperiment & hasOwnName)
            if preexisting_experiment:
                if not load_existing:
                    raise RuntimeError(f'An experiment with the name {ownName} already exists in this database. To connect to it, set load_existing to True. To make a new experiment, please choose a unique name.')
                self.__overwrite_with_document(preexisting_experiment[0])
            else:
                if load_existing:
                    raise Warning(f'An experiment with the name {ownName} does not yet exist in this database. To add this experiment to the database, set load_existing to False.')
                self.ctx.add(self.document)
        if binary_collection:
            self.binary_collection = binary_collection
        return self

    # Document Methods
    @classmethod
    def from_database(cls, db, directory, ndi_query: T.Query):
        documents = db.find(ndi_query=ndi_query)
        return [
            cls.from_document(d, directory) 
            for d in documents 
            if d.metadata['type'] == cls.DOCUMENT_TYPE
        ]
        
    @classmethod
    def from_document(cls, document, directory) -> Experiment:
        """Alternate Experiment constructor. For use whan initializing from a document bytearray.
        ::
            reconstructed_experiment = Experiment.from_document(fb)

        :type document: ndi.Document

        .. currentmodule:: ndi.experiment

        :rtype: :class:`Experiment`
        """
        return cls(
            id_=document.id,
            directory=directory,
            name=document.metadata['name'],
            daq_system_ids=document.data['daq_system_ids']
        )

    # Experiment Methods
    def update(self, name: str) -> None:
        if name:
            self.name = name
        self.ctx.update(self.document, force=True)

    def add_daq_system(self, daq_system: T.DaqSystem) -> None:
        """Stores a daq_system instance and labels it with the experiment's id.

        .. currentmodule:: ndi.daq_system

        :type daq_system: :class:`DaqSystem`
        """
        if isinstance(daq_system, str): 
            # if daq_system is an id
            # this will occur when an experiment is being rebuilt from a document
            daq_system = self.ctx.find_by_id(daq_system)
            if not daq_system:
                raise ValueError(f'A DAQ system with id {daq_system} does not exist in the database.')
            daq_system.metadata['experiment_id'] = self.id
            self.daq_system_ids.append(daq_system)
        else:
            daq_system.metadata['experiment_id'] = self.id
            self.daq_system_ids.append(daq_system.id)
            if self.ctx:
                self.ctx.add(daq_system.document)


    def add_related_obj_to_db(self, ndi_object: T.NdiObjectWithExperimentId) -> None:
        ndi_object.metadata['experiment_id'] = self.id
        ndi_object.ctx = self.ctx
        ndi_object.binary_collection = self.binary_collection
        self.ctx.add(ndi_object.document)

    def add_epoch(self, epoch: T.Epoch):
        if not isinstance(epoch, Epoch):
            raise TypeError(f'Object {epoch} is not an instance of ndi.Epoch.')
        self.__check_foreign_key_requirements(epoch, ['channel_ids', 'daq_system_id'])

        self.add_related_obj_to_db(epoch)

    def add_probe(self, probe: T.Probe):
        if not isinstance(probe, Probe):
            raise TypeError(f'Object {probe} is not an instance of ndi.Probe.')
        self.__check_foreign_key_requirements(probe, ['daq_system_id'])
        
        self.add_related_obj_to_db(probe)

    def add_channel(self, channel: T.Channel):
        if not isinstance(channel, Channel):
            raise TypeError(f'Object {channel} is not an instance of ndi.Channel.')
        self.__check_foreign_key_requirements(channel, ['epoch_ids', 'probe_id', 'daq_system_id'])
        
        self.add_related_obj_to_db(channel)

    def __check_foreign_key_requirements(self, ndi_object, foreign_keys):
        for key in foreign_keys:
            if key.endswith('_ids'):
                related_ids = getattr(ndi_object, key)
                for id_ in related_ids:
                    self.__verify_relation_exists_in_experiment(ndi_object, id_)
            else:
                related_id = getattr(ndi_object, key)
                if not related_id:
                    raise RuntimeError(f'Object {ndi_object} is missing its required {key}.')
                self.__verify_relation_exists_in_experiment(ndi_object, related_id)

    def __verify_relation_exists_in_experiment(self, ndi_object, related_id):
        relation = self.ctx.find_by_id(related_id)
        relation_experiment_id = relation.metadata['experiment_id']
        relation_type = relation.metadata['type']
        if not relation:
            raise RuntimeError(f'Object {ndi_object} appears to have a foreign key to {relation_type}:{related_id}, which does not yet exist. Please add {relation_type}:{related_id} to the experiment before trying again.')
        elif relation_experiment_id != self.metadata['experiment_id']:
            raise RuntimeError(f'Object {ndi_object} appears to have a foreign key to {relation_type}:{related_id}, which belongs to another experiment({relation_experiment_id}).')

    def get_epochs(self):
        return self.get_ndi_dependencies(Epoch)
    def get_probes(self):
        return self.get_ndi_dependencies(Probe)
    def get_channels(self):
        return self.get_ndi_dependencies(Channel)

    def get_ndi_dependencies(self, NdiClass):
        has_this_experiment_id = Q('_metadata.experiment_id') == self.id
        is_desired_class = Q('_metadata.type') == NdiClass.DOCUMENT_TYPE
        documents = self.ctx.find(has_this_experiment_id & is_desired_class)
        ndi_objects = [NdiClass.from_document(d) for d in documents]
        return ndi_objects

    def find_epochs(self, ndi_query):
        return self._find_by_class(Epoch, ndi_query)
    def find_probes(self, ndi_query):
        return self._find_by_class(Probe, ndi_query)
    def find_channels(self, ndi_query):
        return self._find_by_class(Channel, ndi_query)

    def _find_by_class(self, NdiClass, ndi_query):
        class_filter = Q('_metadata.type') == NdiClass.DOCUMENT_TYPE
        docs = self.ctx.find(class_filter & ndi_query)
        return [NdiClass.from_document(d) for d in docs]

    def check_id_in_database(self, id_):
        return bool(self.ctx.find_by_id(id_))

    def check_dependency_exists(self, id_):
        for item in self.dependencies.values():
            if isinstance(item, Document):
                if item.id == id_:
                    return True
            elif item == id_:
                return True
        return False

    def add_document(self, doc, key=None):
        doc.metadata['experiment_id'] = self.id
        doc.set_ctx(self.ctx)
        doc.set_binary_collection(self.binary_collection)
        self.add_dependency(doc, key=key)

    def get_documents(self):
        ndi_object_prefixes = [f'{o.DOCUMENT_TYPE}:' for o in [Epoch, Probe, Channel]]
        # filter out ndi_objects
        documents = {}
