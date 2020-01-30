from ndi import DaqSystem, FileNavigator, Experiment, Epoch
from ndi.daqreaders import MockReader

fn = FileNavigator(['a', 'b'], 'b')

ds1 = DaqSystem('DAQ1', fn, MockReader, 'feoiwnf')

flatbuffer = ds1.serialize()

ds2 = ds1.from_flatbuffer(flatbuffer)

assert ds1 == ds2
assert fn == ds2.file_navigator

e = Epoch()

buf = e.serialize()

e2 = Epoch.from_flatbuffer(buf)

assert e == e2
