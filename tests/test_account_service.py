from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from plat.repository.d_basic import SimpleKVRepository
from plat.service.acc_service import AccountService, ExpiredAccountException
from xtu_ems.ems.session import Session


class TestAccountService(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        account_repository = SimpleKVRepository()
        self.service = AccountService(account_repository=account_repository,
                                      token_repository=SimpleKVRepository())
        AccountService.ems.async_login = AsyncMock(return_value=Session(session_id='session_id'))

    async def test_login(self):
        account = await self.service.login('TestUsername', 'TestPassword')
        self.assertIsNotNone(account)
        self.assertEqual(account.student_id, 'TestUsername')
        self.assertEqual(account.password, 'TestPassword')
        self.assertEqual(account.session, 'session_id')

    async def test_auth_with_token(self):
        account = await self.service.login('TestUsername', 'TestPassword')
        self.assertIsNotNone(account)
        token_account = await self.service.auth_with_token(account.token)
        self.assertIsNotNone(token_account)
        self.assertEqual(account, token_account)

    async def test_expire_account(self):
        account = await self.service.login('TestUsername', 'TestPassword')
        self.assertIsNotNone(account)
        await self.service.expire_account(account.student_id)
        with self.assertRaises(ExpiredAccountException):
            await self.service.auth_with_token(account.token)
