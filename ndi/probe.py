from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object
from .constants import PROBE_DOCUMENT_TYPE, CHANNEL_DOCUMENT_TYPE
from .query import Query as Q


class Probe(NDI_Object):
    """
    A flatbuffer interface for probes.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    DOCUMENT_TYPE = PROBE_DOCUMENT_TYPE

    def __init__(
        self,
        name: str,
        reference: int,
        type_: str,
        id_: T.NdiId = None,
        daq_system_id: T.NdiId = None,
        experiment_id: T.NdiId = None,
    ) -> None:
        """Probe constructor: initializes with fields defined in `ndi_schema <https://>`_'s Probe table. For use when creating a new Probe instance from scratch.
        ::
            new_probe = Probe(**fields)

        :param name:
        :type name: str
        :param reference:
        :type reference: int
        :param type_:
        :type type_: str
        :param id_: defaults to None
        :type id_: str, optional
        :param daq_system_id: defaults to ''
        :type daq_system_id: str, optional
        :raises TypeError: When *type_* is not from the list of :mod:`ndi.probe_type`.
        """
        super().__init__(id_)
        self.metadata['name'] = name
        self.metadata['type'] = self.DOCUMENT_TYPE
        self.metadata['experiment_id'] = experiment_id
        self.add_data_property('reference', reference)
        self.add_data_property('daq_system_id', daq_system_id)
        self.add_data_property('type', type_)

    # Document Methods
    @classmethod
    def from_document(cls, document) -> Probe:
        """Alternate Probe constructor. For use whan initializing from a document.
        ::
            reconstructed_probe = Probe.from_document(fb)

        :type document: ndi.Document

        .. currentmodule:: ndi.probe

        :rtype: :class:`Probe`
        """
        return cls(
            id_=document.id,
            name=document.metadata['name'],
            reference=document.data['reference'],
            type_=document.data['type'],
            daq_system_id=document.data['daq_system_id'],
            experiment_id=document.metadata['experiment_id'],
        )

    def update(
        self,
        name: str,
        reference: int,
        type_: str,
        daq_system_id: T.NdiId = None,
        experiment_id: T.NdiId = None,
    ) -> None:
        if name:
            self.name = name
        if reference:
            self.reference = reference
        if type_:
            self.type_ = type_
        if daq_system_id:
            self.daq_system_id = daq_system_id
        if experiment_id:
            self.experiment_id = experiment_id
        self.ctx.update(self.document, force=True)

    def add_channel(self, channel):
        if channel.metadata['type'] != CHANNEL_DOCUMENT_TYPE:
            raise TypeError(f'Object {channel} is not an instance of ndi.Channel.')
        
        channel.metadata['experiment_id'] = self.metadata['experiment_id']
        channel.probe_id = self.id
        channel.daq_system_id = self.daq_system_id

        channel.ctx = self.ctx
        channel.binary_collection = self.binary_collection
        self.ctx.add(channel.document)

    def get_channels(self):
        is_ndi_channel_type = Q('_metadata.type') == CHANNEL_DOCUMENT_TYPE
        is_related = Q('probe_id') == self.id
        query = is_ndi_channel_type & is_related
        return self.ctx.find(query)

    def get_daq_system(self):
        self.ctx.find_by_id(self.daq_system_id)

    def get_experiment(self):
        self.ctx.find_by_id(self.experiment_id)
