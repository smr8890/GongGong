from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import patch, Mock, AsyncMock

from plat.entity import Account, AccountStatus, TaskEntity
from plat.repository.d_basic import SimpleKVRepository
from plat.task import UpdateTask
from xtu_ems.ems.handler.get_student_courses import StudentCourseGetter


class TestUpdateTask(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.storage = SimpleKVRepository()
        accounts = {
            'test_id1': Account(student_id='test_id1', password='test_password1', session='test_session1',
                                status=AccountStatus.UNDEFINED),
            'test_id2': Account(student_id='test_id2', password='test_password2', session='test_session2',
                                status=AccountStatus.NORMAL)

        }
        self.user_repository = SimpleKVRepository()
        self.user_repository.data.update(accounts)
        validator = Mock()
        validator.async_handler = AsyncMock(return_value=True)
        self.session_validator = validator

    async def test_get_account(self):
        """
        测试获取账户
        """
        with patch.object(StudentCourseGetter, 'async_handler', return_value="Mocked Data"):
            handler = StudentCourseGetter()
            task = UpdateTask(key='TestKey', handler=handler, storage=self.storage,
                              user_repository=self.user_repository)
            task.session_validator = self.session_validator
            await task()

            result: TaskEntity = await self.storage.async_get_item('TestKey')
            self.assertEqual(result.data, "Mocked Data")
