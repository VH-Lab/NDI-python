from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object
import ndi.schema.Channel as build_channel
from ndi.schema.ClockType import ClockType as build_clock_type
from ndi.schema.ChannelType import ChannelType as build_channel_type
from .channel_type import ChannelType
from .clock_type import ClockType


class Channel(NDI_Object):
    """A flatbuffer interface for channels.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    DOCUMENT_TYPE = 'channel'

    # TODO: require daq_system_id after implementing DaqReaders
    def __init__(
        self,
        name: str,
        number: int,
        type_: str,
        source_file: str,
        # NOTE: channels and epochs will almost definitely be a many-to-many relationship
        #       would need a list of epoch_ids
        epoch_id: T.NdiId,
        probe_id: T.NdiId,
        daq_system_id: T.NdiId = None,
        experiment_id: T.NdiId = None,
        id_: T.NdiId = None,
        clock_type: str = 'no_time'
    ) -> None:
        """Channel constructor: initializes with fields defined in `ndi_schema <https://>`_'s Channel table. For use when creating a new Channel instance from scratch.
        ::
            new_channel = Channel(**fields)

        :param name: Abbreviated type with number (e.g. ai21, do3, aux13).
        :type name: str
        :param number: [description]
        :type number: int
        :param type_: One of the types defined in :mod:`ndi.channel_type`.
        :type type_: str
        :param source_file: [description]
        :type source_file: str
        :param epoch_id: [description]
        :type epoch_id: str
        :param probe_id: [description]
        :type probe_id: str
        :param daq_system_id: defaults to '<empty_string>'
        :type daq_system_id: str, optional
        :type id_: str, optional
        :param clock_type: defaults to 'no_time'
        :type clock_type: str, optional

        .. currentmodule:: ndi.channel

        :rtype: :class:`Channel`
        """
        super().__init__(id_)
        self.metadata['name'] = name
        self.metadata['type'] = self.DOCUMENT_TYPE
        self.metadata['experiment_id'] = experiment_id
        self.add_data_property('number', number)
        self.add_data_property('type', type_)
        self.add_data_property('clock_type', clock_type)
        self.add_data_property('source_file', source_file)
        self.add_data_property('epoch_id', epoch_id)
        self.add_data_property('probe_id', probe_id)
        self.add_data_property('daq_system_id', daq_system_id)

    @classmethod
    def from_document(cls, document) -> Channel:
        """Alternate Channel constructor. For use whan initializing from a document.
        ::
            reconstructed_channel = Channel.from_document(fb)

        :type document: ndi.Document

        .. currentmodule:: ndi.channel

        :rtype: :class:`Channel`
        """
        return cls(
            id_=document.id,
            name=document.metadata['name'],
            number=document.data['number'],
            type_=document.data['type'],
            clock_type=document.data['clock_type'],
            source_file=document.data['source_file'],
            epoch_id=document.data['epoch_id'],
            probe_id=document.data['probe_id'],
            daq_system_id=document.data['daq_system_id'],
            experiment_id=document.metadata['experiment_id'],
        )

    def update(
        self,
        name: str,
        number: int,
        type_: str,
        source_file: str,
        epoch_id: T.NdiId,
        probe_id: T.NdiId,
        daq_system_id: T.NdiId = None,
        experiment_id: T.NdiId = None,
        clock_type: str = 'no_time'
    ) -> None:
        if name: self.name = name
        if number: self.number = number
        if type_: self.type = type_
        if source_file: self.source_file = source_file
        if epoch_id: self.epoch_id = epoch_id
        if probe_id: self.probe_id = probe_id
        if daq_system_id: self.daq_system_id = daq_system_id
        if experiment_id: self.experiment_id = experiment_id
        if clock_type: self.clock_type = clock_type

        self.ctx.update(self.document, force=True)
