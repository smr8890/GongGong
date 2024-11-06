import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from xtu_ems.ems.account import AuthenticationAccount
from xtu_ems.ems.ems import QZEducationalManageSystem


class TimedEntity:
    """时间类型的实体类"""

    def __init__(self, data=None):
        self.__dict__['data'] = data
        self.create_time = datetime.now()
        self.update_time = datetime.now()

    def __setattr__(self, key, value):
        """拦截所有属性的设置，更新更新时间为当前时间"""
        self.__dict__['update_time'] = datetime.now()
        self.__dict__[key] = value


class TaskEntity(TimedEntity):
    """任务类型的实体类"""

    def __init__(self, data=None):
        super().__init__(data)
        self.submit_time = None

    def on_submit_task(self):
        """当提交任务，更新提交时间为当前时间"""
        self.__dict__['submit_time'] = datetime.now()


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
    _token: str = uuid.uuid4()
    """用户凭证"""
    session: str = None
    """用户Session"""
    status: AccountStatus = AccountStatus.UNDEFINED
    """账户状态"""
    last_login_time: datetime = datetime.now()
    """最后一次登陆时间"""
    last_use_time: datetime = datetime.now()
    """最后一次使用时间"""

    async def login(self):
        """登陆教务系统并且获取Session"""
        ems = QZEducationalManageSystem()
        account = AuthenticationAccount(username=self.student_id, password=self.password)
        try:
            self.session = (await ems.async_login(account)).session_id
            self.status = AccountStatus.NORMAL
            self.last_login_time = datetime.now()
        except Exception as e:
            self.status = AccountStatus.INVALID
            self.last_login_time = datetime.now()
            raise e

    def __bool__(self):
        """判断用户是否有效"""
        return self.status == AccountStatus.NORMAL

    @property
    def token(self):
        """获取用户凭证"""
        self.last_use_time = datetime.now()
        return self._token
