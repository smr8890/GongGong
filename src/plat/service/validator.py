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
        if item is not None and hasattr(item, 'update_time') and hasattr(item, 'submit_time'):
            now = datetime.now()
            # 更新时间超出并且提交时间也超出才认为数据过期，需要重新获取
            return not (now - item.update_time > self.update_expire and
                        now - item.submit_time > self.submit_expire)
        else:
            return False
