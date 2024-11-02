from datetime import datetime


class TimedEntity:
    """时间类型的实体类"""

    def __init__(self):
        self.create_time = datetime.now()
        self.update_time = datetime.now()

    def __setattr__(self, key, value):
        """拦截所有属性的设置，更新更新时间为当前时间"""
        self.update_time = datetime.now()
        self.__dict__[key] = value


class TaskEntity(TimedEntity):
    """任务类型的实体类"""

    def __init__(self):
        super().__init__()
        self.submit_time = None

    def on_submit_task(self):
        """当提交任务，更新提交时间为当前时间"""
        self.__dict__['submit_time'] = datetime.now()
