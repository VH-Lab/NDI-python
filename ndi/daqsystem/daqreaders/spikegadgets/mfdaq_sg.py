import re
import numpy as np
import os
import xml.etree.ElementTree as ET
from ndi.daqsystem.mfdaq import DaqReaderMultiFunction
from ndi.daqsystem.probe import Probe
from ndi.schema.ChannelType import ChannelType


class ProbeNTrode(Probe):
    """SpikeGadgets NTrode channel"""

    def __init__(self, name, reference):
        self.name = name
        self.reference = reference
        # Auxiliary
        if name[0] == 'A':
            self.type = ChannelType.auxiliary
            if name[1] == 'i':
                self.number = int(name[3:])
            else:
                self.number = int(name[4:])
        elif name[0] == 'D':
            if name[1] == 'i':
                self.type = ChannelType.digital_in
                self.number = int(name[3:])
            else:
                self.type = ChannelType.digital_out
                self.number = int(name[4:])
        elif name.startswith('Tetrode'):
            self.type = ChannelType.analog_in
            self.number = int(name[7:])
        else:
            # MCU (digital inputs)
            self.type = ChannelType.digital_in
            self.number = int(name[7:]) + 32


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
        block_size = self._packet_header_size + 2 + len(self.probes)
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
        for SpikeNTrode in self._spike_configuration.findall('SpikeNTrode'):
            ntrode_id = int(SpikeNTrode.attrib['id'])
            ntrode_channels = SpikeNTrode.findall('SpikeChannel')
            # Add ntrode's to channels
            for ref in range(len(ntrode_channels)):
                ntrode = ProbeNTrode(
                    'Tetrode{}'.format(ntrode_id), ref + 1)
                self.probes.append(ntrode)
        self._file_packet_size = 2 * self._num_channels + self._packet_header_size

    def _read_packet(self):
        """Get the next packet."""
        # Skip to start of actual data
        offset = self._data_offset + self._packet_offset * \
            self._file_packet_size + self._packet_header_size
        # Increment for next packet read
        self._packet_offset += 1
        return np.fromfile(self._file_handle, dtype=np.uint8, count=self._num_channels*2, offset=self._packet_header_size)

    def _read_all_samples(self, channels_to_read):
        channel_size = len(channels_to_read)
        block_size = self._packet_header_size + channel_size
        samples = (self.t1 - self.t0) * self.sample_rate
        timestamps = np.ndarray((channel_size, samples), dtype=np.uint32)
        data = np.ndarray((channel_size, samples), dtype=np.uint16)
        for n in range(channel_size):
            packet = self._read_packet()
            print(packet)
            timestamps[n] = packet.view(dtype=np.uint32)[0]
            channel_offset = 2 + channels_to_read[n]
            data[n] = packet.view(dtype=np.uint16)[
                channel_offset:channel_offset + block_size]
        return data

    def read_channels_epoch_samples(self, channel_type, channels, epoch):
        channels_to_read = []
        if channel_type == ChannelType.analog_in:
            for ch in channels:
                channels_to_read.append(ch.number * 4 + ch.reference)
        else:
            raise Exception('Only ntrode channels are supported')
        self._read_all_samples(channels_to_read)
