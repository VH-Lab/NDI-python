import time
import sys
import numpy as np

class Cache:
    def __init__(self, maxMemory=10e9, replacement_rule='fifo'):
        self.maxMemory = maxMemory
        self.replacement_rule = replacement_rule
        self._table = []

    def _get_item_size(self, data):
        if isinstance(data, np.ndarray):
            return data.nbytes
        return sys.getsizeof(data)

    def add(self, key, type, data, priority=0):
        item_size = self._get_item_size(data)

        if item_size > self.maxMemory:
            raise ValueError("This variable is too large to fit in the cache; cache's maxMemory exceeded.")

        new_entry = {
            'key': key,
            'type': type,
            'timestamp': time.time(),
            'priority': priority,
            'bytes': item_size,
            'data': data
        }

        total_memory = self.bytes() + item_size
        if total_memory > self.maxMemory:
            if self.replacement_rule == 'error':
                raise MemoryError("Cache is too full to accommodate the new data; error was requested rather than replacement.")

            freespace_needed = total_memory - self.maxMemory
            inds_to_remove, is_new_item_safe_to_add = self._evaluate_items_for_removal(freespace_needed, new_entry)

            if is_new_item_safe_to_add:
                self.remove(inds_to_remove)
                self._table.append(new_entry)
        else:
            self._table.append(new_entry)

    def _evaluate_items_for_removal(self, freebytes, new_item):
        table_plus_new = self._table + [new_item]

        # Sort items for eviction: lower priority first, then by rule
        # LIFO: newest first (descending timestamp)
        # FIFO: oldest first (ascending timestamp)
        sort_order_desc = self.replacement_rule == 'lifo'

        # Create a list of tuples for sorting: (priority, timestamp, original_index, bytes)
        sortable_items = [
            (item['priority'], item['timestamp'], i, item['bytes'])
            for i, item in enumerate(table_plus_new)
        ]

        # Sort by priority (ascending), then by timestamp
        sortable_items.sort(key=lambda x: (x[0], x[1]), reverse=False)
        if sort_order_desc:
            # For LIFO, we need to reverse the timestamp sort but keep priority ascending
            sortable_items.sort(key=lambda x: x[0], reverse=False) # sort by priority
            sortable_items.sort(key=lambda x: x[1], reverse=True) # then sort by time


        cumulative_memory_saved = 0
        inds_to_remove_all = []
        for item in sortable_items:
            cumulative_memory_saved += item[3]
            inds_to_remove_all.append(item[2])
            if cumulative_memory_saved >= freebytes:
                break

        new_item_index = len(table_plus_new) - 1
        is_new_item_safe_to_add = new_item_index not in inds_to_remove_all

        # We can only remove items that are actually in the cache
        inds_to_remove = [i for i in inds_to_remove_all if i < len(self._table)]

        return inds_to_remove, is_new_item_safe_to_add

    def remove(self, index_or_key, type=None):
        indices_to_remove = []
        if isinstance(index_or_key, list): # it's a list of indices
            indices_to_remove = sorted(index_or_key, reverse=True)
        elif isinstance(index_or_key, int):
            indices_to_remove = [index_or_key]
        else: # it's a key
            for i, item in enumerate(self._table):
                if item['key'] == index_or_key and item['type'] == type:
                    indices_to_remove.append(i)

        for index in indices_to_remove:
            self._table.pop(index)

    def clear(self):
        self._table = []

    def lookup(self, key, type):
        for item in self._table:
            if item['key'] == key and item['type'] == type:
                return item
        return None

    def bytes(self):
        if not self._table:
            return 0
        return sum(item['bytes'] for item in self._table)
