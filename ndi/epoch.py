from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object
import ndi.schema.Epoch as build_epoch


class Epoch(NDI_Object):
    """
    A flatbuffer interface for epochs.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """
    # TODO: require daq_system_id after implementing DaqReaders

    DOCUMENT_TYPE = 'epoch'

    def __init__(
        self, 
        daq_system_id: T.NdiId = None, 
        experiment_id: T.NdiId = None, 
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
        self.daq_system_id = daq_system_id

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
            daq_system_id=document.data['daq_system_id'],
            experiment_id=document.metadata['experiment_id'],
        )

    def update(
        self, 
        daq_system_id: T.NdiId = None, 
        experiment_id: T.NdiId = None, 
    ) -> None:
        if daq_system_id: self.daq_system_id = daq_system_id
        if experiment_id: self.experiment_id = experiment_id

        self.ctx.update(self.document, force=True)