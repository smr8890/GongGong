import json
import os
from unittest import TestCase

from xtu_ems.ems.handler.get_classroom_status import ClassroomStatusGetter, ClassroomStatusGetterTomorrow

username = os.getenv("XTU_USERNAME")
password = os.getenv("XTU_PASSWORD")


class TestClassroomStatusGetter(TestCase):
    def test_handler(self):
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = ClassroomStatusGetter()
        resp = handler.handler(session)
        print(json.dumps(resp, indent=4, ensure_ascii=False, default=str))
        self.assertIsNotNone(resp)


class TestClassroomStatusGetterTomorrow(TestCase):
    def test_handler(self):
        from xtu_ems.ems.account import AuthenticationAccount
        from xtu_ems.ems.ems import QZEducationalManageSystem
        account = AuthenticationAccount(username=username,
                                        password=password)
        ems = QZEducationalManageSystem()
        session = ems.login(account)
        handler = ClassroomStatusGetterTomorrow()
        resp = handler.handler(session)
        print(json.dumps(resp, indent=4, ensure_ascii=False, default=str))
        self.assertIsNotNone(resp)
