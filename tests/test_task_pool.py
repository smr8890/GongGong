import os
from unittest import TestCase

from xtu_ems.ems.account import AuthenticationAccount
from xtu_ems.ems.ems import QZEducationalManageSystem
from xtu_ems.ems.handler.get_student_exam import StudentExamGetter

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestAsyncTaskPool(TestCase):
    def test_run(self):
        from plat.task_pool import AsyncTaskPool
        pool = AsyncTaskPool(max_workers=30)
        account = AuthenticationAccount(username=username,
                                        password=password)

        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = StudentExamGetter()
        for _ in range(99):
            pool.add_task(handler.async_handler(session))
        pool.run(verbose=True)
        self.assertTrue(True)
