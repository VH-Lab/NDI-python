from ..util.vlt import data as vlt_data

class Param:
    def __init__(self):
        pass

    def numepochs(self):
        return len(self.epochtable())

    def epochtable(self):
        # caching logic will go here
        return self.buildepochtable()

    def buildepochtable(self):
        return []

    def get_cache(self):
        return None, None

    def reset_epoch_table(self):
        pass

    def matched_epoch_table(self, hashvalue):
        pass

    def epoch_id(self, epoch_number):
        pass

    def epoch_table_entry(self, epoch_number):
        pass

    def epoch_clock(self, epoch_number):
        pass

    def t0_t1(self, epoch_number):
        pass

    def epoch2str(self, number):
        pass

    def epoch_nodes(self):
        pass

    def epochsetname(self):
        return 'unknown'

    def underlying_epoch_nodes(self, epochnode):
        pass

    def epoch_graph(self):
        pass

    def build_epoch_graph(self):
        pass

    def cached_epoch_graph(self):
        pass

    def is_sync_graph_root(self):
        return True
