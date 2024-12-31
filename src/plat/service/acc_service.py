import asyncio
import logging

from plat.repository.d_basic import KVRepository, SimpleKVRepository
from plat.service.entity import Account, AccountStatus
from xtu_ems.ems.account import AuthenticationAccount
from xtu_ems.ems.ems import QZEducationalManageSystem, InvalidAccountException
from xtu_ems.ems.handler.valid_session import SessionValidator
from xtu_ems.ems.session import Session

logger = logging.getLogger('task.refresh')


class ExpiredAccountException(Exception):
    """账户已过期"""

    def __init__(self, username):
        self.username = username


class BannedAccountException(Exception):
    """账户已被封禁"""

    def __init__(self, username):
        self.username = username


class AccountService:
    ems = QZEducationalManageSystem()
    session_validator = SessionValidator()

    def __init__(self, account_repository: KVRepository[str, Account],
                 token_repository: KVRepository[str, Account] = SimpleKVRepository()):
        """
        账户服务类
        Args:
            account_repository: 账户存储库
            token_repository: token存储库
        """
        self.account_repository = account_repository
        self.token_repository = token_repository

    async def login(self, username: str, password: str):
        """
        登陆教务系统

        当登陆校务系统后，之前的token会被覆盖，并且返回一个新的token
        Args:
            username: 用户名
            password: 密码

        Returns:
            登录成功的账户信息
        """
        # 尝试从本地账户存储库中获取账户信息
        authed_account: Account = await self.account_repository.async_get_item(username)
        if authed_account and authed_account.is_valid():
            # 若本地账户存在且有效，检查密码是否匹配
            if authed_account.password != password:
                raise InvalidAccountException()
            return authed_account
        # 若本地账户不存在或失效，使用 AuthenticationAccount 进行登录操作
        account = AuthenticationAccount(username=username, password=password)
        session = await self.ems.async_login(account)
        if authed_account:
            # 若本地有账户，更新其信息
            authed_account.password = password
            authed_account.session = session.session_id
            authed_account.status = AccountStatus.NORMAL
        else:
            # 若本地没有账户，创建新账户
            authed_account = Account(student_id=username,
                                     password=password,
                                     session=session.session_id,
                                     status=AccountStatus.NORMAL)
        # 保存更新后的账户信息
        authed_account = await self.save_account_with_uni_token(authed_account)
        return authed_account

    async def save_account_with_uni_token(self, account: Account):
        """
        刷新唯一的token来保存用户

        Args:
            account: 用户信息

        Returns:
            用户信息
        """
        # 将之前的token删除
        old_token = account.token
        if old_token:
            await self.token_repository.async_del_item(old_token)
        # 创建新的token，保证token的唯一性
        while await self.token_repository.async_get_item(account.token):
            account.refresh_token()
        await self.token_repository.async_set_item(account.token, account)
        await self.account_repository.async_set_item(account.student_id, account)
        return account

    async def auth_with_token(self, token: str):
        """
        用token验证用户
        Args:
            token: 用户凭证

        Returns:
            验证通过的用户信息
        """
        account: Account = await self.token_repository.async_get_item(token)
        if account and account.token == token:
            if account.status == AccountStatus.EXPIRED:
                raise ExpiredAccountException(account.student_id)
            elif account.status == AccountStatus.BANNED:
                raise BannedAccountException(account.student_id)
            elif account.status == AccountStatus.NORMAL:
                return account
        else:
            return None

    async def expire_account(self, username: str):
        """
        标记过期用户

        Args:
            username: 用户名

        Returns:
            过期的用户信息
        """
        account: Account = await self.account_repository.async_get_item(username)
        if account:
            account.status = AccountStatus.EXPIRED
            await self.account_repository.async_set_item(username, account)
            return account
        else:
            return None

    async def refresh_task(self):
        logger.info(f"一共有 {len(self.account_repository)} 个账户需要刷新")
        valid_account_count = 0
        async for student_id in self.account_repository:
            account: Account = await self.account_repository.async_get_item(student_id)
            if account.is_valid():
                result = await self.refresh_single_session(account)
                if not result:
                    logger.warning(f"账户 {account.student_id} 刷新session失败")
                    await self.expire_account(account.student_id)
                else:
                    logger.debug(f"账户 {account.student_id} 刷新session成功")
                    valid_account_count += 1
                await asyncio.sleep(.5)
        logger.info(f"已刷新 {valid_account_count}/{len(self.account_repository)} 个账户")

    async def refresh_session(self, interval: int):
        """
        刷新session
        """

        while True:
            logger.info('开始刷新session')
            asyncio.create_task(self.refresh_task())
            await asyncio.sleep(interval)

    async def refresh_single_session(self, account: Account, max_retry=3) -> bool:
        """
        刷新单个session
        Args:
            account: 账号信息
            max_retry: 最大重试次数

        Returns:
            bool: 是否刷新成功
        """
        retry = 0
        while retry <= max_retry:
            try:
                validation = await self.session_validator.async_handler(Session(session_id=account.session))
                return validation
            except Exception as e:
                retry += 1
                logger.warning(f'账户 {account.student_id} 刷新session失败 [{retry} / {max_retry}]')
                logger.error("账号保活时异常", exc_info=True)

        return False
