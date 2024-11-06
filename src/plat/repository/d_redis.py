from typing import TypeVar, Callable, Union, AsyncIterator

from redis.asyncio import Redis

from plat.repository.d_basic import KVRepository

_KEY = Union[bytes, str, memoryview]
_VAL = TypeVar('_VAL')


class RedisRepository(KVRepository[_KEY, _VAL]):
    class DefaultSerializer:
        """默认序列化器"""

        def __call__(self, value: _VAL) -> bytes:
            if hasattr(value, 'redis_encode'):
                return value.redis_encode()
            if hasattr(value.__class__, 'redis_encode'):
                return value.__class__.redis_encode(value)
            return value

    class DefaultDeserializer:
        """默认反序列化器"""

        def __call__(self, value: bytes | str) -> _VAL:
            if value is None:
                return value
            if hasattr(_VAL, 'redis_decode'):
                return _VAL.redis_decode(value)
            if hasattr(_VAL.__class__, 'redis_decode'):
                return _VAL.__class__.redis_decode(value)
            if isinstance(_VAL, str):
                return value.decode()
            return value.decode()

    def __init__(self,
                 redis: Redis = None,
                 serialize: Callable[[_VAL], bytes | str] = None,
                 deserialize: Callable[[bytes | str], _VAL] = None):
        """
        初始化Redis存储类
        Args:
            redis: Redis连接对象
            serialize: 序列化器，`VAL` => `bytes|str`
            deserialize: 反序列化器， `bytes|str` => `VAL`
        """
        self.redis = redis or Redis.from_url('redis://localhost:6379/0')
        self.serializer = serialize or RedisRepository.DefaultSerializer()
        self.deserializer = deserialize or RedisRepository.DefaultDeserializer()

    async def close(self):
        await self.redis.aclose()

    async def async_get_item(self, key: _KEY):
        value = await self.redis.get(key)
        return self.deserializer(value)

    async def async_set_item(self, key: _KEY, value: _VAL):
        value = self.serializer(value)
        await self.redis.set(key, value)

    class Iterator(AsyncIterator):
        def __init__(self, redis: Redis, pattern: str = '*'):
            """
            Initializes an iterator for Redis keys matching the given pattern.
            Args:
                redis: Redis connection object
                pattern: Pattern to match keys (default '*')
            """
            self.redis = redis
            self.pattern = pattern
            self._cursor = 0
            self._keys = []

        async def __anext__(self) -> _KEY:
            # Fetch the next batch of keys if we have exhausted the current batch
            if not self._keys:
                self._cursor, self._keys = await self.redis.scan(cursor=self._cursor, match=self.pattern)
                # If no more keys and cursor is back to zero, we are done
                if not self._keys and self._cursor == 0:
                    raise StopAsyncIteration

            # Return the next key
            return self._keys.pop(0)

    def __aiter__(self) -> AsyncIterator[_KEY]:
        """
        Allows RedisRepository to be used as an asynchronous iterator.
        Iterates over keys in the Redis database that match the specified pattern.
        """
        return RedisRepository.Iterator(self.redis, '*')

    async def async_del_item(self, key: _KEY):
        await self.redis.delete(key)
