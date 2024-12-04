import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TimedEntity:
    """时间类型的实体类"""

    def __init__(self, data=None):
        self.data = data
        self.create_time = datetime.now()
        self.update_time = None

    def update(self, key, value):
        self.__dict__[key] = value
        self.update_time = datetime.now()


class TaskEntity(TimedEntity):
    """任务类型的实体类"""

    def __init__(self, data=None):
        super().__init__(data)
        self.submit_time = None

    def on_submit_task(self):
        """当提交任务，更新提交时间为当前时间"""
        self.submit_time = datetime.now()


class AccountStatus(Enum):
    """用户状态"""
    NORMAL = 1
    """正常"""
    EXPIRED = 2
    """过期，需要重新登陆"""
    BANNED = 3
    """禁止使用"""
    INVALID = 4
    """无效，需要重新登陆"""
    UNDEFINED = 5
    """未定义"""


class Account(BaseModel):
    """用户类"""

    student_id: str
    """学号"""
    password: str
    """密码"""
    _token: str = None
    """用户凭证"""
    session: str = None
    """用户Session"""
    status: AccountStatus = AccountStatus.UNDEFINED
    """账户状态"""
    last_login_time: datetime = datetime.now()
    """最后一次登陆时间"""

    @property
    def token(self):
        """生成用户凭证"""
        if self._token is None:
            self._token = str(uuid.uuid4())
        return self._token

    def is_valid(self):
        """判断用户是否有效"""
        return self.status == AccountStatus.NORMAL

    def refresh_token(self):
        """刷新用户凭证"""
        self._token = str(uuid.uuid4())
        return self.token
