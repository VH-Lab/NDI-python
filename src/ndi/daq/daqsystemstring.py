from ..util.vlt import string as vlt_string

class DaqSystemString:
    def __init__(self, devicename, channeltype=None, channellist=None):
        if channeltype is None and channellist is None:
            self.devicename, self.channeltype, self.channellist = self._parse_string(devicename)
        else:
            self.devicename = devicename
            self.channeltype = channeltype
            self.channellist = channellist

    def _parse_string(self, devstr):
        devicename = ''
        channeltype = []
        channellist = []

        devstr = devstr.replace(' ', '')
        parts = devstr.split(':')
        devicename = parts[0]

        if len(parts) > 1:
            channel_info = parts[1]
            for segment in channel_info.split(';'):
                if not segment:
                    continue

                match = None
                for i, char in enumerate(segment):
                    if char.isdigit():
                        match = i
                        break

                if match is not None:
                    ctype = segment[:match]
                    cnums_str = segment[match:]
                    cnums = vlt_string.str2intseq(cnums_str)
                    channeltype.extend([ctype] * len(cnums))
                    channellist.extend(cnums)

        return devicename, channeltype, channellist

    def __str__(self):
        s = f"{self.devicename}:"

        if not self.channellist:
            return s

        # This logic is complex and will require a more detailed implementation
        # For now, a simplified version:

        temp_channels = {}
        for ctype, cnum in zip(self.channeltype, self.channellist):
            if ctype not in temp_channels:
                temp_channels[ctype] = []
            temp_channels[ctype].append(cnum)

        segments = []
        for ctype, cnums in temp_channels.items():
            segments.append(f"{ctype}{vlt_string.intseq2str(cnums)}")

        s += ";".join(segments)

        return s
