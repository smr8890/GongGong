import asyncio
from abc import abstractmethod
from datetime import timedelta
from typing import TypeVar, Generic

from plat.entity import TaskEntity
from plat.repository.d_basic import KVRepository, SimpleKVRepository
from plat.repository.d_cache import CacheRepository
from plat.task import PersonalUpdateTask
from plat.validator import TaskValidator
from xtu_ems.ems.handler import Handler

D = TypeVar('D')


class IService(Generic[D]):
    @abstractmethod
    async def get_info(self, student_id: str) -> D | None:
        pass


class PersonalInfoService(IService[D]):

    async def get_info(self, student_id: str) -> D | None:
        task: TaskEntity = await self.storage.async_get_item(student_id)
        return task.data

    def __init__(self, handler: Handler,
                 update_expire: timedelta,
                 submit_expire: timedelta,
                 account_repository: KVRepository):
        self.validator = TaskValidator(update_expire=update_expire,
                                       submit_expire=submit_expire)
        self.handler = handler
        self.account_repository = account_repository
        self.background_tasks = set()

        async def on_update(key, value):
            pass

        async def on_refresh(key: str, value: TaskEntity, repo: KVRepository[str, TaskEntity]):
            session = await self.account_repository.async_get_item(key)
            if session:
                personal_task = PersonalUpdateTask(key, self.handler, repo, self.account_repository)
                if not value:
                    value = TaskEntity()
                value.on_submit_task()
                task = asyncio.create_task(personal_task())
                await repo.async_set_item(key, value)
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)
            return value

        self.storage: [str, TaskEntity] = CacheRepository(local_cache=SimpleKVRepository[str, TaskEntity](),
                                                          validator=self.validator,
                                                          on_write_back=on_update,
                                                          on_refresh=on_refresh)
