import asyncio
import logging

from plat.repository.d_basic import KVRepository
from plat.service.entity import TaskEntity, Account, AccountStatus
from xtu_ems.ems.handler import Handler
from xtu_ems.ems.handler.valid_session import SessionValidator
from xtu_ems.ems.session import Session

logger = logging.getLogger('task.update')


class UpdateTask:
    session_validator = SessionValidator()

    def __init__(self, key: str,
                 handler: Handler,
                 storage: KVRepository[str, TaskEntity],
                 user_repository: KVRepository[str, Account]):
        """
        后台更新的任务
        Args:
            key: 持久化名称
            handler: 更新的具体操作，需要实现async_handler方法
            storage: 存储更新后的结果
            user_repository: 存储用户的仓库，用于设置用户状态
        """
        self.key = key
        self.storage = storage
        self.handler = handler
        self.user_repository = user_repository
        logger.info(f"创建了一个更新任务: [{handler.__class__.__name__}]-[{key}]")

    async def get_account(self) -> Account:
        """
        获取Session
        Returns:

        """
        async for user_id in self.user_repository:
            account = await self.user_repository.async_get_item(user_id)
            return account

    async def _try_handler(self, session: Session, max_retry=3):
        """
        尝试执行handler
        Args:
            session:
            max_retry:

        Returns:

        """
        retry = 0
        while retry <= max_retry:
            try:
                result = await self.handler.async_handler(session)
                return result
            except Exception as e:
                retry += 1
                logger.warning(f"重试第 [{retry} / {retry}] 次")
                if retry >= max_retry:
                    raise e
                await asyncio.sleep(.1)

    async def __call__(self, *args, **kwargs):
        # 获取Session，并且判断Session是否存在
        account = await self.get_account()
        if account:
            session = account.session
            try:
                result = await self._try_handler(Session(session_id=session))
            except Exception as e:
                # 认为Session可能过期了
                logger.info(f" {account.student_id} 的SESSION可能过期了，需要重新登陆")
                logging.error("Exception occurred", exc_info=True)
                account.status = AccountStatus.EXPIRED
                return None
            # 更新数据
            former_record: TaskEntity = ((await self.storage.async_get_item(self.key))
                                         or TaskEntity())
            former_record.update(key='data', value=result)
            await self.storage.async_set_item(self.key, former_record)
            return result
        return None


class PersonalUpdateTask(UpdateTask):
    def __init__(self, student_id: str,
                 handler: Handler,
                 storage: KVRepository[str, TaskEntity],
                 user_repository: KVRepository[str, Account]):
        """
        后台更新的任务
        Args:
            student_id: 更新使用的学号，更新的任务会使用这个学号对应的SESSION
            handler: 更新的具体操作，需要实现async_handler方法
            storage: 存储更新后的结果
            user_repository: 存储用户的仓库，用于设置用户状态
        """
        super().__init__(student_id, handler, storage, user_repository)

    async def get_account(self) -> Account:
        """
        获取Session
        Returns:

        """
        account = await self.user_repository.async_get_item(self.key)
        return account
