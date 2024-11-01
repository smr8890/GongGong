from typing import TypeVar, Callable

from redis.asyncio import Redis

from plat.repository.d_basic import KVRepository

_DATA = TypeVar('_DATA')


class RedisRepository(KVRepository[_DATA]):
    """redis存储类"""

    class DefaultSerializer:
        """默认序列化器"""

        def __call__(self, value: _DATA) -> bytes:
            if hasattr(value, 'redis_encode'):
                return value.redis_encode()
            if hasattr(value.__class__, 'redis_encode'):
                return value.__class__.redis_encode(value)
            return value

    class DefaultDeserializer:
        """默认反序列化器"""

        def __call__(self, value: bytes) -> _DATA:
            if value is None:
                return value
            if hasattr(_DATA, 'redis_decode'):
                return _DATA.redis_decode(value)
            if hasattr(_DATA.__class__, 'redis_decode'):
                return _DATA.__class__.redis_decode(value)
            if isinstance(_DATA, str):
                return value.decode()
            return value.decode()

    def __init__(self,
                 redis: Redis = None,
                 serialize: Callable[[_DATA], bytes | str] = None,
                 deserialize: Callable[[bytes], _DATA] = None):
        """
        初始化Redis存储类
        Args:
            redis: Redis连接对象
            serialize: 序列化器，DATA => bytes|str
            deserialize: 反序列化器， bytes => DATA
        """
        self.redis = redis or Redis.from_url('redis://localhost:6379/0')
        self.serializer = serialize or RedisRepository.DefaultSerializer()
        self.deserializer = deserialize or RedisRepository.DefaultDeserializer()

    async def close(self):
        await self.redis.aclose()

    async def async_get_item(self, key):
        value = await self.redis.get(key)
        return self.deserializer(value)

    async def async_set_item(self, key, value):
        value = self.serializer(value)
        await self.redis.set(key, value)
