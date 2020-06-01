from __future__ import annotations
import ndi.types as T
from .ndi_object import NDI_Object
from .channel import Channel
from .epoch import Epoch
from .probe import Probe


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
        epoch_probe_map_class,
        epoch_ids = [],
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
        self.add_data_property('epoch_ids', epoch_ids)
        # TODO: figure out how to handle these as documents (pending daq sys)
        self.file_navigator = file_navigator
        self.epoch_probe_map_class = epoch_probe_map_class
        self.daq_reader = daq_reader

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
            epoch_ids=document.data['epoch_ids'],
            file_navigator=None,
            epoch_probe_map_class=None,
            daq_reader=lambda id: None,
        )

    def provision(self, experiment: T.Experiment):
        if self.id not in experiment.daq_systems:
            experiment.add_daq_system(self)

        epoch_sets = self.file_navigator.get_epoch_set(experiment.directory)
        epochprobemap = self.epoch_probe_map_class(
            daq_reader=self.daq_reader,
            epoch_sets=epoch_sets,
            daq_system_id=self.id,
            experiment_id=experiment.id,
            ctx=self.ctx
        )

        epochs, probes, channels = epochprobemap.get_epochs_probes_channels()
        for epoch in epochs:
            self.epoch_ids.append(epoch.id)
        self.epochs = epochs
        self.probes = probes
        self.channels = channels
        for ndi_object in epochs + probes + channels:
            self.ctx.upsert(ndi_object.document, force=True)

    def get_epochs(self):
        return self.epochs

    def get_probes(self):
        return self.probes

    def get_channels(self):
        return self.channels
