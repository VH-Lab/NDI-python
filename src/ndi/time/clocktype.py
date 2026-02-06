
class ClockType:
    def __init__(self, type):
        self.set_clock_type(type)

    def set_clock_type(self, type):
        valid_types = [
            'utc', 'approx_utc', 'exp_global_time', 'approx_exp_global_time',
            'dev_global_time', 'approx_dev_global_time', 'dev_local_time',
            'no_time', 'inherited'
        ]
        if type.lower() not in valid_types:
            raise ValueError(f"Unknown clock type '{type}'")
        self.type = type.lower()

    def epoch_graph_edge(self, other):
        # depends on ndi.time.timemapping
        return float('inf'), None

    def needs_epoch(self):
        return self.type == 'dev_local_time'

    def __str__(self):
        return self.type

    def __eq__(self, other):
        if isinstance(other, ClockType):
            return self.type == other.type
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def assert_global(clocktype_obj):
        if not ClockType.is_global(clocktype_obj):
            raise AssertionError("Clock type must be a global type.")

    @staticmethod
    def is_global(clocktype_obj):
        valid_types = [
            'utc', 'approx_utc', 'exp_global_time', 'approx_exp_global_time',
            'dev_global_time', 'approx_dev_global_time'
        ]
        return clocktype_obj.type in valid_types
