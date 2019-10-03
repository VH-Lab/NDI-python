import re
import numpy as np
import xml.etree.ElementTree as ET
from ndi.daqsystem.mfdaq import DaqReaderMultiFunction
from ndi.daqsystem.probe import Probe


class ProbeNTrode(Probe):
    """SpikeGadgets NTrode probe."""
    # Maybe these should just be the native types?
    type = 'n-trode'

    def __init__(self, ntrode_id, channel_count, lfp_channel, ref_on, ref_chan, filter_on, low_filter=None, high_filter=None):
        self.id = ntrode_id
        self.channels = channel_count
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
    def channels(self):
        # Get channel refs from parsed config
        return int(self._hardware_configuration.attrib['numChannels'])

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
        return ET.fromstring(configuration_doc)

    def _setup_channels(self):
        """Setup channel readers based on SpikeConfiguration portion of configuration."""
        devices = self._hardware_configuration.findall('Device')
        devices.sort(key=lambda dev: dev.attrib['packetOrderPreference'])
        for SpikeNTrode in self._spike_configuration.findall('SpikeNTrode'):
            ntrode_id = int(SpikeNTrode.attrib['id'])
            ntrode_channels = SpikeNTrode.findall('SpikeChannel')
            channel_count = len(ntrode_channels)
            lfp_channel = int(SpikeNTrode.attrib['LFPChan'])
            ref_on = bool(SpikeNTrode.attrib['refOn'])
            ref_chan = int(SpikeNTrode.attrib['refChan'])
            filter_on = bool(SpikeNTrode.attrib['filterOn'])
            if filter_on:
                low_filter = int(SpikeNTrode.attrib['lowFilter'])
                high_filter = int(SpikeNTrode.attrib['highFilter'])
            ntrode = ProbeNTrode(ntrode_id, channel_count, lfp_channel,
                                 ref_on, ref_chan, filter_on, low_filter, high_filter)
            self.probes.append(ntrode)
        self._file_packet_size = 2 * self.channels + self._packet_header_size

    def _readPacket(self):
        """Get the next packet."""
        self._packet_offset += 1
        # Skip to start of actual data
        self._file_handle.seek(self._data_offset +
                               self._packet_offset * self._file_packet_size)
        return self._file_handle.read(self._file_packet_size)

    def get_channels_epoch(self):
        pass

    def read_channels_epoch_samples(self):
        pass

    def get_epoch_probe_map(self):
        pass
