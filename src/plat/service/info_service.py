import asyncio
from abc import abstractmethod
from datetime import timedelta
from typing import TypeVar, Generic

from plat.repository.d_basic import KVRepository, SimpleKVRepository
from plat.repository.d_cache import CacheRepository
from plat.service.entity import TaskEntity
from plat.service.task import UpdateTask, PersonalUpdateTask
from plat.service.validator import TaskValidator
from xtu_ems.ems.handler import Handler

D = TypeVar('D')


class IService(Generic[D]):
    @abstractmethod
    async def get_info(self, student_id: str) -> D | None:
        pass


class PersonalInfoService(IService[D]):
    """个人信息服务"""

    async def get_info(self, key: str) -> D | None:
        task: TaskEntity = await self.storage.async_get_item(key)
        return task.data

    def generate_task(self, key: str,
                      storage: KVRepository[str, TaskEntity]):
        """

        Args:
            key: 更新内容的key
            storage: 本地存储

        Returns:
            返回一个更新任务
        """
        return PersonalUpdateTask(key, self.handler, storage, self.account_repository)

    def get_refresher(self):
        async def on_refresh(key: str, value: TaskEntity, repo: KVRepository[str, TaskEntity]):
            task = self.generate_task(key=key, storage=repo)
            if not value:
                value = TaskEntity()
            value.on_submit_task()
            task = asyncio.create_task(task())
            await repo.async_set_item(key, value)
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
            return value

        return on_refresh

    def get_updater(self):
        async def on_update(key, value):
            pass

        return on_update

    def __init__(self, handler: Handler,
                 update_expire: timedelta,
                 submit_expire: timedelta,
                 account_repository: KVRepository):
        self.validator = TaskValidator(update_expire=update_expire,
                                       submit_expire=submit_expire)
        self.handler = handler
        self.account_repository = account_repository
        self.background_tasks = set()
        self.storage: [str, TaskEntity] = CacheRepository(local_cache=SimpleKVRepository[str, TaskEntity](),
                                                          validator=self.validator,
                                                          on_write_back=self.get_updater(),
                                                          on_refresh=self.get_refresher())


class PublicInfoService(PersonalInfoService[D]):
    """公共信息服务"""

    async def get_info(self, student_id: str = None) -> D | None:
        task: TaskEntity = await self.storage.async_get_item(self.name)
        return task.data

    async def get_public_info(self) -> D | None:
        return await self.get_info()

    def generate_task(self, key: str,
                      storage: KVRepository[str, TaskEntity]):
        """

        Args:
            key: 更新内容的key
            storage: 本地存储

        Returns:
            返回一个更新任务
        """
        return UpdateTask(key, self.handler, storage, self.account_repository)

    def __init__(self,
                 handler: Handler,
                 update_expire: timedelta,
                 submit_expire: timedelta,
                 account_repository: KVRepository,
                 name: str = "data"):
        super().__init__(handler, update_expire, submit_expire, account_repository)
        self.name = name
