from ndi import DaqSystem, FileNavigator, Experiment, Epoch

fn = FileNavigator(['a', 'b'], 'b')

ds1 = DaqSystem('DAQ1', fn, 'DaqReader', 'feoiwnf')

buffer = ds1.serialize()

ds2 = ds1.frombuffer(buffer)

assert ds1 == ds2
assert fn == ds2.file_navigator

e = Epoch()

buf = e.serialize()

e2 = Epoch.frombuffer(buf)

assert e == e2
