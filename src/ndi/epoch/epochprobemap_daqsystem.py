from .epochprobemap import EpochProbeMap
from ..util.vlt import data as vlt_data
from ..util.vlt import string as vlt_string

class EpochProbeMapDaqSystem(EpochProbeMap):
    def __init__(self, name, reference, type, devicestring, subjectstring):
        super().__init__()

        vlt_data.islikevarname(name)
        self.name = name

        if not (isinstance(reference, int) and reference >= 0):
            raise ValueError("reference must be a non-negative integer.")
        self.reference = reference

        vlt_data.islikevarname(type)
        self.type = type

        vlt_data.islikevarname(devicestring)
        self.devicestring = devicestring

        self.subjectstring = subjectstring

    def serialization_struct(self):
        return {
            'name': self.name,
            'reference': self.reference,
            'type': self.type,
            'devicestring': self.devicestring,
            'subjectstring': self.subjectstring
        }

    def serialize(self):
        st = self.serialization_struct()
        fn = list(st.keys())
        s = '\t'.join(fn) + '\n'

        row = []
        for f in fn:
            val = st[f]
            if isinstance(val, (str, int, float)):
                row.append(str(val))
        s += '\t'.join(row) + '\n'
        return s

    def savetofile(self, filename):
        with open(filename, 'w') as f:
            f.write(self.serialize())

    @staticmethod
    def decode(s):
        st = []
        lines = s.splitlines()
        if len(lines) < 2:
            return st

        fields = lines[0].split('\t')
        for i in range(1, len(lines)):
            st.append(vlt_string.tabstr2struct(lines[i], fields))
        return st
