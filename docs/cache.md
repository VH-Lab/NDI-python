# ndi.cache

The `ndi.cache` module provides a simple in-memory cache for storing data.

## The `Cache` class

The `Cache` class is used to create a new cache object.

### `__init__(self, maxMemory=10e9, replacement_rule='fifo')`

Creates a new cache object.

*   `maxMemory`: The maximum amount of memory (in bytes) that the cache can use.
*   `replacement_rule`: The replacement rule to use when the cache is full. Can be `'fifo'`, `'lifo'`, or `'error'`.

### `add(self, key, type, data, priority=0)`

Adds an item to the cache.

*   `key`: The key for the item.
*   `type`: The type of the item.
*   `data`: The data to be cached.
*   `priority`: The priority of the item (higher priority items are less likely to be evicted).

### `lookup(self, key, type)`

Looks up an item in the cache.

*   `key`: The key for the item.
*   `type`: The type of the item.

Returns the cached item, or `None` if the item is not found.
