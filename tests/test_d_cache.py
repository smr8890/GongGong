from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock

from plat.repository.d_basic import SimpleKVRepository
from plat.repository.d_cache import CacheRepository


class TestAsyncCacheRepository(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.orign_db = SimpleKVRepository()
        self.validator = MagicMock(return_value=True)
        self.on_update = AsyncMock()
        self.on_refresh = AsyncMock(return_value='RemoteValue')
        self.cache_db = CacheRepository(local_cache=SimpleKVRepository(), validator=self.validator,
                                        on_refresh=self.on_refresh, on_write_back=self.on_update)
        await self.cache_db.local_cache.async_set_item('TestKey', 'TestValue')
        await self.orign_db.async_set_item('TestKey', 'TestValue')

    async def test_async_get_item_with_exist_item(self):
        """异步测试获取存在的键值"""
        self.assertEqual('TestValue', await self.cache_db.async_get_item('TestKey'))
        self.validator.assert_called_once_with('TestValue')

    async def test_async_set_item(self):
        """异步测试设置键值"""
        await self.cache_db.async_set_item('TestKey1', 'TestValue1')
        self.assertEqual('TestValue1', await  self.cache_db.async_get_item('TestKey1'))
        self.on_update.assert_called_once_with('TestKey1', 'TestValue1')

    async def test_async_get_item_with_not_exist_item(self):
        """异步测试获取不存在的键值"""
        self.validator.return_value = False
        self.assertEqual('RemoteValue', await self.cache_db.async_get_item('TestKey2'))
        self.validator.assert_called_once_with(None)
        self.on_refresh.assert_called_once_with('TestKey2', None, self.cache_db.local_cache)
