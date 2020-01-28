from .ndi_object import NDI_Object
from .file_navigator import FileNavigator
import ndi.schema.DaqSystem as build_daq_system
import ndi.daqreaders as DaqReaders


class DaqSystem(NDI_Object):
    def __init__(self, name, file_navigator, daq_reader, experiment_id=None, id_=None):
        super().__init__(id_)
        self.name = name
        self.file_navigator = file_navigator
        self.daq_reader = daq_reader
        self.experiment_id = experiment_id

    @classmethod
    def from_flatbuffer(cls, flatbuffer):
        daq_system = build_daq_system.DaqSystem.GetRootAsDaqSystem(
            flatbuffer, 0)
        return cls._reconstruct(daq_system)

    @classmethod
    def _reconstruct(cls, daq_system):
        file_navigator = FileNavigator._reconstruct(daq_system.FileNavigator())
        daq_reader = getattr(DaqReaders, daq_system.DaqReader().decode('utf8'))

        return cls(id_=daq_system.Id().decode('utf8'),
                   name=daq_system.Name().decode('utf8'),
                   file_navigator=file_navigator,
                   daq_reader=daq_reader,
                   experiment_id=daq_system.ExperimentId().decode('utf8'))

    def _build(self, builder):
        id_ = builder.CreateString(self.id)
        name = builder.CreateString(self.name)
        file_navigator = self.file_navigator._build(builder)
        daq_reader = builder.CreateString(self.daq_reader.__name__)
        experiment_id = builder.CreateString(self.experiment_id)

        build_daq_system.DaqSystemStart(builder)
        build_daq_system.DaqSystemAddId(builder, id_)
        build_daq_system.DaqSystemAddName(builder, name)
        build_daq_system.DaqSystemAddFileNavigator(builder, file_navigator)
        build_daq_system.DaqSystemAddDaqReader(builder, daq_reader)
        build_daq_system.DaqSystemAddExperimentId(builder, experiment_id)
        return build_daq_system.DaqSystemEnd(builder)
