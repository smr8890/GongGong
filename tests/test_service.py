import asyncio
from datetime import timedelta
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import patch

from plat.entity import Account, AccountStatus
from plat.repository.d_basic import SimpleKVRepository
from plat.service import PersonalInfoService, PublicInfoService
from xtu_ems.ems.handler.get_student_courses import StudentCourseGetter
from xtu_ems.ems.handler.get_teaching_calendar import TeachingCalendarGetter
from xtu_ems.ems.handler.valid_session import SessionValidator

session_repository = SimpleKVRepository()
acc = Account(student_id='Mock Username', session='Mock Session', status=AccountStatus.NORMAL,
              password='Mock Password')
session_repository.data.update({acc.student_id: acc})


class TestPersonalInfoService(IsolatedAsyncioTestCase):
    async def test_get_info(self):
        """测试获取个人信息"""
        with patch.object(StudentCourseGetter, 'async_handler', return_value="Mocked Data"):
            with patch.object(SessionValidator, 'async_handler', return_value=True):
                handler = StudentCourseGetter()
                service = PersonalInfoService(handler=handler, update_expire=timedelta(days=1),
                                              submit_expire=timedelta(seconds=10),
                                              account_repository=session_repository)
                result = await service.get_info(acc.student_id)
                self.assertIsNone(result)
                # 如果数据没有更新，需要等待
                if not await service.get_info(acc.student_id):
                    await asyncio.sleep(.1)
                result = await service.get_info(acc.student_id)
                self.assertEqual('Mocked Data', result)
                # assert handler 的被调此书为1
                self.assertEqual(1, handler.async_handler.call_count)

    async def test_get_info_with_expired(self):
        """测试获取个人信息，但是老数据过期"""
        with patch.object(StudentCourseGetter, 'async_handler', return_value="Mocked Data"):
            with patch.object(SessionValidator, 'async_handler', return_value=True):
                handler = StudentCourseGetter()
                service = PersonalInfoService(handler=handler, update_expire=timedelta(microseconds=1),
                                              submit_expire=timedelta(microseconds=1),
                                              account_repository=session_repository)
                result = await service.get_info(acc.student_id)
                self.assertIsNone(result)
                # 如果数据没有更新，需要等待
                await asyncio.sleep(.1)
                result = await service.get_info(acc.student_id)
                self.assertIsNotNone(result)
                await asyncio.sleep(.1)
                # assert handler 的被调此书为2
                self.assertEqual(2, handler.async_handler.call_count)


class TestPublicInfoService(IsolatedAsyncioTestCase):
    async def test_get_info(self):
        """获取公共信息"""
        with patch.object(TeachingCalendarGetter, 'async_handler', return_value="Mocked Data"):
            with patch.object(SessionValidator, 'async_handler', return_value=True):
                handler = TeachingCalendarGetter()
                service = PublicInfoService(name='calendar', handler=handler, update_expire=timedelta(days=1),
                                            submit_expire=timedelta(seconds=10),
                                            account_repository=session_repository)
                result = await service.get_info('calendar')
                self.assertIsNone(result)
                # 如果数据没有更新，需要等待
                if not await service.get_info('calendar'):
                    await asyncio.sleep(.1)
                result = await service.get_info('calendar')
                self.assertEqual('Mocked Data', result)
                # assert handler 的被调此书为1
                self.assertEqual(1, handler.async_handler.call_count)

    async def test_get_info_with_expired(self):
        """测试获取公共信息，但是老数据过期"""
        with patch.object(TeachingCalendarGetter, 'async_handler', return_value="Mocked Data"):
            with patch.object(SessionValidator, 'async_handler', return_value=True):
                handler = TeachingCalendarGetter()
                service = PublicInfoService(name='calendar', handler=handler, update_expire=timedelta(microseconds=1),
                                            submit_expire=timedelta(microseconds=1),
                                            account_repository=session_repository)
                result = await service.get_info('calendar')
                self.assertIsNone(result)
                # 如果数据没有更新，需要等待
                await asyncio.sleep(.1)
                result = await service.get_info('calendar')
                self.assertIsNotNone(result)
                await asyncio.sleep(.1)
                # assert handler 的被调此书为2
                self.assertEqual(2, handler.async_handler.call_count)
