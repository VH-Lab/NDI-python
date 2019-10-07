import re
import numpy as np
import os
import xml.etree.ElementTree as ET
from ndi.daqsystem.mfdaq import DaqReaderMultiFunction
from ndi.daqsystem.probe import Probe
from ndi.schema.ProbeChannel import ProbeChannel
from ndi.schema.ChannelType import ChannelType


class SpikeGadgetChannel(ProbeChannel):
    """SpikeGadgets channel"""

    def __init__(self, name):
        # Auxiliary
        if name[0] == 'A':
            self.type = ChannelType.auxiliary
            if name[1] == 'i':
                self.number = int(name[3:])
                self.name = 'axn{}'.format(self.number)
            else:
                self.number = int(name[4:])
                self.name = 'axo{}'.format(self.number)
        elif name[0] == 'D':
            if name[1] == 'i':
                self.type = ChannelType.digital_in
                self.number = int(name[3:])
                self.name = 'di{}'.format(self.number)
            else:
                self.type = ChannelType.digital_out
                self.number = int(name[4:])
                self.name = 'do{}'.format(self.number)
        elif name.startswith('Tetrode'):
            self.type = ChannelType.analog_in
            self.number = int(name[7:])
            self.name = 'ai{}'.format(self.number)
        else:
            # MCU (digital inputs)
            self.type = ChannelType.digital_in
            self.number = int(name[7:]) + 32
            self.name = 'di{}'.format(self.number)


class ProbeNTrode(Probe):
    """SpikeGadgets NTrode probe."""
    # Maybe this should just be a native type?
    type = 'n-trode'
    channel_type = ChannelType.analog_in

    def __init__(self, ntrode_id, channels, lfp_channel, ref_on, ref_chan, filter_on, low_filter=None, high_filter=None):
        self.id = ntrode_id
        self.channels = channels
        self.lfp_channel = lfp_channel
        self.ref_on = ref_on
        self.ref_chan = ref_chan
        self.filter_on = filter_on
        self.low_filter = low_filter
        self.high_filter = high_filter

    @property
    def name(self):
        return 'Tetrode{}'.format(self.id)

    @property
    def reference(self):
        return self.id


class DaqReaderMultiFunctionSg(DaqReaderMultiFunction):
    """
    This class reads data from video files .rec that spikegadgets use

    This implementation does not use the Trodes live API and only works with prerecorded data at the original sample rate.

    Spike Gadgets: http://spikegadgets.com/
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # File region to read per step
        self._file_packet_size = -1
        # Start of data relative to start of file
        self._data_offset = -1
        # Counter for the current packet
        self._packet_offset = 0
        # Bytes for packet header
        self._packet_header_size = 4  # TODO: This can be overriden?
        # Open and parse file
        self._file_handle = open(self.path, 'rb')
        self._configuration = self._read_configuration()
        self._setup_channels()

    @property
    def _hardware_configuration(self):
        # Shortcut for hardware configuration tag
        return self._configuration.find('HardwareConfiguration')

    @property
    def _spike_configuration(self):
        # Shortcut for spike configuration
        return self._configuration.find('SpikeConfiguration')

    @property
    def _num_channels(self):
        # Get channel count from parsed config
        return int(self._hardware_configuration.attrib['numChannels'])

    @property
    def t0(self):
        return 0

    @property
    def t1(self):
        block_size = self._packet_header_size + 2 + len(self.channels)
        total_samples = self._data_size / block_size
        return int((total_samples - 1) / self.sample_rate)

    @property
    def sample_rate(self):
        # Get sample rate from parsed config
        return int(self._hardware_configuration.attrib['samplingRate'])

    def _read_configuration(self):
        """Read in and parse the configuration XML prefix."""
        configuration_doc = ''
        for line in self._file_handle:
            decoded_line = line.decode('ascii')
            configuration_doc += decoded_line
            # End of XML header
            if '</Configuration>' in decoded_line:
                self._data_offset = self._file_handle.tell()
                break
        # Calculate data bytes here
        file_size = os.fstat(self._file_handle.fileno()).st_size
        self._data_size = file_size - self._data_offset
        return ET.fromstring(configuration_doc)

    def _setup_channels(self):
        """Setup channel readers based on SpikeConfiguration portion of configuration."""
        devices = self._hardware_configuration.findall('Device')
        devices.sort(key=lambda dev: dev.attrib['packetOrderPreference'])
        for device in devices:
            for channel in device.findall('Channel'):
                self.channels.append(SpikeGadgetChannel(channel.attrib['id']))
        # Save count for ntrode channel offsets later
        base_channels = len(self.channels)
        for SpikeNTrode in self._spike_configuration.findall('SpikeNTrode'):
            ntrode_id = int(SpikeNTrode.attrib['id'])
            ntrode_channels = SpikeNTrode.findall('SpikeChannel')
            lfp_channel = int(SpikeNTrode.attrib['LFPChan'])
            ref_on = bool(SpikeNTrode.attrib['refOn'])
            ref_chan = int(SpikeNTrode.attrib['refChan'])
            filter_on = bool(SpikeNTrode.attrib['filterOn'])
            if filter_on:
                low_filter = int(SpikeNTrode.attrib['lowFilter'])
                high_filter = int(SpikeNTrode.attrib['highFilter'])
            # Add ntrode's to channels
            probe_channels = []
            for ntrode_ch in ntrode_channels:
                channel_obj = SpikeGadgetChannel(
                    'Tetrode{}'.format(ntrode_id + base_channels))
                probe_channels.append(channel_obj)
                self.channels.append(channel_obj)
            ntrode = ProbeNTrode(ntrode_id, probe_channels, lfp_channel,
                                 ref_on, ref_chan, filter_on, low_filter, high_filter)
            self.probes.append(ntrode)
        self._file_packet_size = 2 * self._num_channels + self._packet_header_size

    def _read_packet(self, reset=False):
        """Get the next packet."""
        self._packet_offset += 1
        if reset:
            # Skip to start of actual data
            self._file_handle.seek(self._data_offset +
                                   self._packet_offset * self._file_packet_size)
        return self._file_handle.read(self._file_packet_size)

    def _read_all_samples(self, channels_to_read):
        first_packet = False
        dtype = np.dtype('uint32')
        channel_size = len(channels_to_read)
        samples = (self.t1 - self.t0) * self.sample_rate
        data = np.ndarray((channel_size, samples), dtype=dtype)
        for n in range(samples):
            packet = self._read_packet()
        return data

    def read_channels_epoch_samples(self, channel_type, channel, epoch):
        channels_to_read = []
        for ch in self.channels:
            if ch.name in channel and ch.type == channel_type:
                channels_to_read.append(ch)
        return self._read_all_samples(channels_to_read)
