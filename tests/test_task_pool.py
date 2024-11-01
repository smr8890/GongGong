from unittest import TestCase
from unittest.mock import AsyncMock


class TestAsyncTaskPool(TestCase):
    def test_run(self):
        """测试异步任务池"""
        total_task = 99
        total_worker = 7
        from plat.task_pool import AsyncTaskPool
        pool = AsyncTaskPool(max_workers=total_worker)
        handler = AsyncMock()
        [pool.add_task(handler()) for _ in range(total_task)]
        pool.run(verbose=True)
        self.assertEqual(total_task, handler.call_count)
