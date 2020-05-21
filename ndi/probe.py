from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object
import ndi.schema.Probe as build_probe
from ndi.schema.ProbeType import ProbeType as build_probe_type
from .probe_type import ProbeType


class Probe(NDI_Object):
    """
    A flatbuffer interface for probes.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    DOCUMENT_TYPE = 'probe'

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
        if type_ in ProbeType:
            self.add_data_property('type', type_)
        else:
            raise TypeError(f'Type must be in {ProbeType}')

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