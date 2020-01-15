from ndi import NDI_Object, DaqSystem, Database
from uuid import uuid4
import ndi.build.Experiment as build_experiment


class Experiment(NDI_Object):
    def __init__(self, reference, databases, daq_systems, unique_reference=uuid4().hex):
        self.reference = reference
        self.unique_reference = unique_reference
        self.databases = databases
        self.daq_systems = daq_systems

    @classmethod
    def frombuffer(cls, buffer):
        experiment = build_experiment.Experiment.GetRootAsExperiment(buffer, 0)
        return cls._reconstruct(experiment)

    @classmethod
    def _reconstruct(cls, experiment):
        databases = Database._reconstructList(experiment)
        daq_systems = DaqSystem._reconstructList(experiment)
        return cls(reference=experiment.Reference().decode('utf8'),
                   databases=databases,
                   daq_systems=daq_systems)

    def _build(self, builder):
        reference = builder.CreateString(self.reference)
        unique_reference = builder.CreateString(self.unique_reference)
        databases = self._buildVector(builder, self.databases)
        daq_systems = self._buildVector(builder, self.daq_systems)

        build_experiment.ExperimentStart(builder)
        build_experiment.ExperimentAddReference(builder, reference)
        build_experiment.ExperimentAddUniqueReference(builder, unique_reference)
        build_experiment.ExperimentAddDatabases(builder, databases)
        build_experiment.ExperimentAddDaqSystems(builder, daq_systems)
        return build_experiment.ExperimentEnd(builder)
