from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object
from uuid import uuid4
import ndi.schema.Experiment as build_experiment


class Experiment(NDI_Object):
    """
    A flatbuffer interface for experiments.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    DOCUMENT_TYPE = 'experiment'

    def __init__(self, name: str, daq_systems: T.List[T.DaqSystem] = [], id_: T.NdiId = None):
        """Experiment constructor: initializes with fields defined in `ndi_schema <https://>`_'s Experiment table. For use when creating a new Experiment instance from scratch.
        ::
            new_experiment = Experiment(**fields)

        .. currentmodule:: ndi.daq_system

        :param name: [description]
        :type name: str
        :param daq_systems: a list of daq_system instances, defaults to []
        :type daq_systems: List[:class:`DaqSystem`], optional
        :param id_: = defaults to None
        :type id_: str, optional
        """
        super().__init__(id_)
        self.metadata['name'] = name
        self.metadata['type'] = self.DOCUMENT_TYPE
        self.metadata['experiment_id'] = self.id
        self.add_data_property('daq_systems', [])
        for daq_system in daq_systems:
            self.add_daq_system(daq_system)

    def connect(self, database=None, binary_collection=None):

        print('connecting')
        print(self)
        print('---')
        if database: 
            print('database')
            print(self.ctx)
            self.ctx = database
            print('-')
            print(self.ctx)
            print('---')
        if binary_collection:
            print('binary_collection')
            print(self.binary_collection)
            self.binary_collection = binary_collection
            print('-')
            print(self.binary_collection)
        return self

    # Document Methods
    @classmethod
    def from_database(cls, db, ndi_query: T.Query):
        documents = db.find(ndi_query=ndi_query)
        return [
            cls.from_document(d) 
            for d in documents 
            if d.metadata['type'] == cls.DOCUMENT_TYPE
        ]
        
    @classmethod
    def from_document(cls, document) -> Experiment:
        """Alternate Experiment constructor. For use whan initializing from a document bytearray.
        ::
            reconstructed_experiment = Experiment.from_document(fb)

        :type document: ndi.Document

        .. currentmodule:: ndi.experiment

        :rtype: :class:`Experiment`
        """
        return cls(
            id_=document.id,
            name=document.metadata['name'],
            daq_systems=document.data['daq_systems']
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
        if isinstance(daq_system, str): # if daq_system is an id
            self.daq_systems.append(daq_system)
        else:
            daq_system.experiment_id = self.id
            self.daq_systems.append(daq_system.id)
            if self.ctx:
                self.ctx.add(daq_system.document)


    def add_related_obj_to_db(self, obj: T.NdiObjectWithExperimentId, key = None) -> None:
        obj.metadata['experiment_id'] = self.id
        self.add_dependency(obj.document, key=key)

    add_probe = add_related_obj_to_db
    add_channel = add_related_obj_to_db
    add_epoch = add_related_obj_to_db
    
    def add_document(self, doc, key=None):
        doc.metadata['experiment_id'] = self.id
        self.add_dependency(doc, key=key)
