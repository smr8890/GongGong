from typing import TypeVar, Callable, Union

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
