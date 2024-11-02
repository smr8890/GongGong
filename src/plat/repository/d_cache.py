import asyncio
from typing import TypeVar, Callable, Awaitable

from plat.repository.d_basic import KVRepository
from plat.validator import Validator

_KEY = TypeVar('_KEY')
_VAL = TypeVar('_VAL')


class CacheRepository(KVRepository[_KEY, _VAL]):
    """二级缓存存储类"""

    async def close(self):
        await self.local_cache.close()

    async def async_get_item(self, key: _KEY):
        # 获取本地数据
        local_record = await self.local_cache.async_get_item(key)
        # 如果数据有效则返回
        if self.validator(local_record):
            return local_record
        else:
            # 否则刷新数据
            res = await self.on_refresh(key, local_record, self.local_cache)
            return res

    async def async_set_item(self, key: _KEY, value: _VAL):
        await asyncio.create_task(self.local_cache.async_set_item(key, value))
        await asyncio.create_task(self.on_update(key, value))

    def __init__(self,
                 local_cache: KVRepository[_KEY, _VAL],
                 validator: Validator[_VAL],
                 on_write_back: Callable[[_KEY, _VAL], Awaitable[None]],
                 on_refresh: Callable[[_KEY, _VAL, KVRepository[_KEY, _VAL]], Awaitable[_VAL]],
                 ):

        """

        Args:
            local_cache: 本地存储
            validator: 数据验证器
            on_write_back: 数据回写器
            on_refresh: 数据刷新器
        """

        super().__init__()
        self.on_update = on_write_back
        self.local_cache = local_cache
        self.validator = validator
        self.on_refresh = on_refresh
