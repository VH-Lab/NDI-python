from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object
from .file_navigator import FileNavigator
import ndi.schema.DaqSystem as build_daq_system
import ndi.daqreaders as DaqReaders


class DaqSystem(NDI_Object):
    """
    A flatbuffer interface for DAQ systems.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    DOCUMENT_TYPE = 'daq-system'

    def __init__(
        self,
        name: str,
        file_navigator: T.FileNavigator,
        daq_reader: T.DaqReader,
        experiment_id: T.NdiId = None,
        id_: T.NdiId = None
    ) -> None:
        """DaqSystem constructor: initializes with fields defined in `ndi_schema <https://>`_'s DaqSystem table. For use when creating a new DaqSystem instance from scratch.
        ::
            new_daq_system = DaqSystem(**fields)

        .. currentmodule:: ndi.file_navigator

        :param name: [description]
        :type name: str
        :param file_navigator: [description]
        :type file_navigator: :class:`FileNavigator`
        :param daq_reader: Name of DaqReader class used to read files from FileNavigator.
        :type daq_reader: str
        :param experiment_id: defaults to None
        :type experiment_id: str, optional
        :param id_: defaults to None
        :type id_: str, optional
        """
        super().__init__(id_)
        self.metadata['name'] = name
        self.metadata['type'] = self.DOCUMENT_TYPE
        self.metadata['experiment_id'] = experiment_id

        # TODO: figure out how to handle these as documents (pending daq sys)
        self.file_navigator = file_navigator
        self.add_daq_reader(daq_reader)
        

    @classmethod
    def from_document(cls, document) -> DaqSystem:
        """Alternate DaqSystem constructor. For use whan initializing from a document.
        ::
            reconstructed_daq_system = DaqSystem.from_document(fb)

        :type document: ndi.Document

        .. currentmodule:: ndi.daq_system

        :rtype: :class:`DaqSystem`
        """

        return cls(
            id_=document.id,
            name=document.metadata['name'],
            experiment_id=document.metadata['experiment_id'],
            file_navigator=None,
            daq_reader=lambda id: None,
        )

    def add_daq_reader(self, daq_reader: T.DaqReader) -> None:
        self.daq_reader = daq_reader(self.id)

    def provision(self, experiment: T.Experiment) -> None:
        if self not in experiment.daq_systems:
            experiment.add_daq_system(self)

        # NOTE: This is where the channels, probes, and epochs would all be added 
        # to the database as a part of the given experiment.

        # NOTE: I think this is also where the daq system will add itself to the database 
        #   (if it's not already in it)

        
