import asyncio
import os
from unittest import TestCase

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestZQEducationalManageSystem(TestCase):
    def test_login(self):
        """测试登录"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        self.assertIsNotNone(session)

    def test_async_login(self):
        """测试异步登录"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        res = asyncio.run(ems.async_login(account))
        self.assertIsNotNone(res)

    def test_invalid_account(self):
        """测试无效账户"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username='invalid_username',
                                        password='invalid_password')
        ems = QZEducationalManageSystem()
        from xtu_ems.ems.ems import InvalidAccountException
        with self.assertRaises(InvalidAccountException):
            ems.login(account)

    def test_invalid_async_login(self):
        """异步测试无效账户"""
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username='invalid_username',
                                        password='invalid_password')
        ems = QZEducationalManageSystem()
        from xtu_ems.ems.ems import InvalidAccountException
        with self.assertRaises(InvalidAccountException):
            asyncio.run(ems.async_login(account))
