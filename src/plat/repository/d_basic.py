from abc import abstractmethod
from typing import TypeVar, Generic

_KEY = TypeVar('_KEY')
_VAL = TypeVar('_VAL')


class KVRepository(Generic[_KEY, _VAL]):
    """
    键值存储仓库

    - 实现了__aenter__和__aexit__方法，使得可以使用async with语句
    - 实现了close方法，使得可以关闭连接
    """

    @abstractmethod
    def __aiter__(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @abstractmethod
    async def close(self):
        """关闭连接"""
        pass

    @abstractmethod
    async def async_get_item(self, key: _KEY):
        """异步获取键值"""
        pass

    @abstractmethod
    async def async_set_item(self, key: _KEY, value: _VAL):
        """异步设置键值"""
        pass

    @abstractmethod
    async def async_del_item(self, key: _KEY):
        """异步删除键值"""
        pass

    @abstractmethod
    def __len__(self):
        """异步获取键值"""
        pass


class SimpleKVRepository(KVRepository[_KEY, _VAL]):
    """简单键值存储仓库"""

    def __init__(self):
        self.data: dict[_KEY, _VAL] = {}
        self._iterator = None  # To keep track of the iterator for __anext__

    async def close(self):
        pass

    async def async_get_item(self, key: _KEY):
        return self.data.get(key)

    async def async_set_item(self, key: _KEY, value: _VAL):
        self.data[key] = value

    async def async_del_item(self, key: _KEY):
        """异步删除键值"""
        if key in self.data:
            del self.data[key]

    def __aiter__(self):
        """Return an asynchronous iterator for the keys in the repository."""
        self._iterator = iter(self.data)
        return self

    async def __anext__(self):
        """Asynchronously return the next key in the iteration."""
        try:
            return next(self._iterator)
        except StopIteration:
            raise StopAsyncIteration

    def __len__(self):
        return len(self.data)
