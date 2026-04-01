from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from part4_oop.interfaces import Cache, HasCache, Policy, Storage

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class DictStorage(Storage[K, V]):
    _data: dict[K, V] = field(default_factory=dict, init=False)

    def set(self, key: K, value: V) -> None:
        self._data[key] = value

    def get(self, key: K) -> V | None:
        return self._data.get(key)

    def exists(self, key: K) -> bool:
        return key in self._data

    def remove(self, key: K) -> None:
        if self.exists(key):
            del self._data[key]

    def clear(self) -> None:
        self._data.clear()


@dataclass
class FIFOPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key not in self._order:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LRUPolicy(Policy[K]):
    capacity: int = 5
    _order: list[K] = field(default_factory=list, init=False)

    def register_access(self, key: K) -> None:
        if key in self._order:
            self._order.remove(key)
            self._order.append(key)
        else:
            self._order.append(key)

    def get_key_to_evict(self) -> K | None:
        if len(self._order) > self.capacity:
            return self._order[0]
        return None

    def remove_key(self, key: K) -> None:
        self._order.remove(key)

    def clear(self) -> None:
        self._order.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._order) > 0


@dataclass
class LFUPolicy(Policy[K]):
    capacity: int = 5
    _key_counter: dict[K, int] = field(default_factory=dict, init=False)

    def register_access(self, key: K) -> None:
        if key in self._key_counter:
            self._key_counter.update({key: self._key_counter.get(key) + 1})
        else:
            self._key_counter.update({key: 1})

    def get_key_to_evict(self) -> K | None:
        if len(self._key_counter) > self.capacity:
            min_requests = max(self._key_counter.values()) + 1
            key_to_delete = None
            for key in self._key_counter:
                key_count = self._key_counter[key]
                last_added_key = list(self._key_counter)[-1]
                if key_count < min_requests and key != last_added_key:
                    min_requests = self._key_counter[key]
                    key_to_delete = key
            return key_to_delete
        return None

    def remove_key(self, key: K) -> None:
        del self._key_counter[key]

    def clear(self) -> None:
        self._key_counter.clear()

    @property
    def has_keys(self) -> bool:
        return len(self._key_counter) > 0


class MIPTCache(Cache[K, V]):
    def __init__(self, storage: Storage[K, V], policy: Policy[K]) -> None:
        self.storage = storage
        self.policy = policy

    def set(self, key: K, value: V) -> None:
        self.storage.set(key, value)
        self.policy.register_access(key)
        if self.policy.get_key_to_evict() is not None:
            key_to_delete = self.policy.get_key_to_evict()
            self.storage.remove(key_to_delete)
            self.policy.remove_key(key_to_delete)

    def get(self, key: K) -> V | None:
        self.policy.register_access(key)
        return self.storage.get(key)

    def exists(self, key: K) -> bool:
        return self.storage.exists(key)

    def remove(self, key: K) -> None:
        if self.exists(key):
            self.storage.remove(key)
            self.policy.remove_key(key)

    def clear(self) -> None:
        self.storage.clear()
        self.policy.clear()


class CachedProperty[V]:
    def __init__(self, func: Callable[..., V]) -> None:
        self._func = func

    def __get__(self, instance: HasCache[Any, Any] | None, owner: type) -> V:
        if instance is None:
            return self
        key = self._func.__name__
        if instance.cache.exists(key):
            return instance.cache.get(key)
        value = self._func(instance)
        instance.cache.set(key, value)
        return value
