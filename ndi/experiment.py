from .ndi_object import NDI_Object
from uuid import uuid4
import ndi.schema.Experiment as build_experiment


class Experiment(NDI_Object):
    def __init__(self, name, daq_systems=[], id_=None):
        super().__init__(id_)
        self.name = name
        self.daq_systems = []
        for daq_system in daq_systems:
            self.add_daq_system(daq_system)

    # Flatbuffer Methods
    @classmethod
    def frombuffer(cls, buffer):
        experiment = build_experiment.Experiment.GetRootAsExperiment(buffer, 0)
        return cls._reconstruct(experiment)

    @classmethod
    def _reconstruct(cls, experiment):
        return cls(id_=experiment.Id().decode('utf8'),
                   name=experiment.Name().decode('utf8'))

    def _build(self, builder):
        id_ = builder.CreateString(self.id)
        name = builder.CreateString(self.name)

        build_experiment.ExperimentStart(builder)
        build_experiment.ExperimentAddId(builder, id_)
        build_experiment.ExperimentAddName(builder, name)
        return build_experiment.ExperimentEnd(builder)

    # Experiment Methods
    def add_daq_system(self, daq_system):
        daq_system.experiment_id = self.id
        self.daq_systems.append(daq_system)
