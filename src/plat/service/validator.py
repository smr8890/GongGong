from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Generic, TypeVar

from plat.service.entity import TimedEntity, TaskEntity

_DATA = TypeVar('_DATA')


class Validator(Generic[_DATA]):
    """数据验证器"""

    @abstractmethod
    def validate(self, item: _DATA) -> bool:
        """
        验证数据是否有效
        Args:
            item: 数据

        Returns:
            bool: 是否有效
        """
        pass

    def __call__(self, item: _DATA) -> bool:
        return self.validate(item)


class ExpireValidator(Validator[TimedEntity]):
    """保质期类型的数据有效验证器"""

    def __init__(self, expire: timedelta):
        self.expire: timedelta = expire
        """设置的过期时间"""

    def validate(self, item: TimedEntity) -> bool:
        return datetime.now() - item.update_time < self.expire


class TaskValidator(Validator[TaskEntity]):
    """任务类型的数据有效验证器"""

    def __init__(self, update_expire: timedelta, submit_expire: timedelta):
        self.update_expire: timedelta = update_expire
        self.submit_expire: timedelta = submit_expire

    def validate(self, item: TaskEntity) -> bool:
        if item is None:
            return False
        now = datetime.now()
        if item.submit_time and now - item.submit_time > self.submit_expire:
            # 如果任务已经提交，并且提交时间超过了限制，那么认为任务已经过期，可以检查数据是否更新
            # 此时如果数据更新了，且在有效范围内，则通过验证
            return item.update_time and now - item.update_time < self.update_expire
        return True
