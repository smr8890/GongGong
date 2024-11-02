import asyncio
from abc import abstractmethod
from typing import TypeVar, Generic

_KEY = TypeVar('_KEY')
_VAL = TypeVar('_VAL')


class KVRepository(Generic[_KEY, _VAL]):
    """
    键值存储仓库

    - 实现了__getitem__和__setitem__方法，使得可以像字典一样使用
    - 实现了__aenter__和__aexit__方法，使得可以使用async with语句
    - 实现了close方法，使得可以关闭连接
    """

    def __get_loop(self):
        if hasattr(self, 'loop') and self.loop is not None:
            return self.loop
        else:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
        return self.loop

    def __run_async(self, coroutine):
        loop = self.__get_loop()
        return loop.run_until_complete(coroutine)

    def __getitem__(self, item: _KEY):
        return self.__run_async(self.async_get_item(item))

    def __setitem__(self, key: _KEY, value: _VAL):
        self.__run_async(self.async_set_item(key, value))

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


class SimpleKVRepository(KVRepository[_KEY, _VAL]):
    """简单键值存储仓库"""

    def __init__(self):
        self.data: dict[_KEY, _VAL] = {}

    async def close(self):
        pass

    async def async_get_item(self, key: _KEY):
        return self.data.get(key)

    async def async_set_item(self, key: _KEY, value: _VAL):
        self.data[key] = value
