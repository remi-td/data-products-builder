from cachetools import TTLCache
from functools import wraps
from typing import Callable

_cache: TTLCache = TTLCache(maxsize=512, ttl=60)


def ttl_cached(key_fn: Callable):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            k = key_fn(*a, **kw)
            if k in _cache:
                return _cache[k]
            v = fn(*a, **kw)
            _cache[k] = v
            return v

        return wrapper

    return deco
