from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object


class Epoch(NDI_Object):
    """
    A flatbuffer interface for epochs.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """
    # TODO: require daq_system_id after implementing DaqReaders

    DOCUMENT_TYPE = 'ndi_epoch'

    def __init__(
        self, 
        experiment_id: T.NdiId = None,
        reference_dir: str = '',
        daq_systems = [],
        id_: T.NdiId = None
    ) -> None:
        """Epoch constructor: initializes with fields defined in `ndi_schema <https://>`_'s Epoch table. For use when creating a new Epoch instance from scratch.
        ::
            new_epoch = Epoch(**fields)

        :param daq_system_id: defaults to ''
        :type daq_system_id: str, optional
        :param id_: defaults to None
        :type id_: str, optional
        """
        super().__init__(id_)
        self.metadata['type'] = self.DOCUMENT_TYPE
        self.metadata['experiment_id'] = experiment_id
        self.add_data_property('reference_dir', reference_dir)
        self.add_data_property('daq_system_id', daq_system_id)

    @classmethod
    def from_document(cls, document) -> Epoch:
        """Alternate Epoch constructor. For use whan initializing from a document.
        ::
            reconstructed_epoch = Epoch.from_document(fb)

        :type document: ndi.Document

        .. currentmodule:: ndi.epoch

        :rtype: :class:`Epoch`
        """
        return cls(
            id_=document.id,
            experiment_id=document.metadata['experiment_id'],
        )
    
    def add_daq_system(self, daq_system_id):
        self.daq_systems.append(daq_system_id)

    def update(self, experiment_id: T.NdiId = None) -> None:
        if experiment_id: self.experiment_id = experiment_id
        self.ctx.update(self.document, force=True)
