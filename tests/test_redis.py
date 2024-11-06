import unittest

from fakeredis import FakeAsyncRedis

from plat.repository.d_redis import RedisRepository


class TestAsyncRedisRepository(unittest.IsolatedAsyncioTestCase):
    """Redis 存储测试"""

    async def asyncSetUp(self):
        """初始化Redis存储类"""
        self.repo = RedisRepository(redis=FakeAsyncRedis())

    async def asyncTearDown(self):
        """关闭Redis连接"""
        await self.repo.close()

    async def test_async_set_item(self):
        """测试异步设置键值"""
        key, value = "test_key", "test_value"
        await self.repo.async_set_item(key, value)
        # 检查是否设置成功
        self.assertEqual(await self.repo.redis.get(key), value.encode("utf-8"))

    async def test_async_get_item(self):
        """测试异步获取键值"""
        key, value = "test_key", "test_value"
        await self.repo.redis.set(key, value)  # 预先在 Redis 中设置键值
        result = await self.repo.async_get_item(key)
        self.assertEqual(result, value)

    async def test_async_get_item_nonexistent_key(self):
        """测试异步获取不存在的键值"""
        # 检查不存在的键
        result = await self.repo.async_get_item("nonexistent_key")
        self.assertIsNone(result)

    async def test_close(self):
        """测试关闭连接"""
        await self.repo.close()
        self.assertIsNone(self.repo.redis.connection)  # 检查连接是否已关闭
