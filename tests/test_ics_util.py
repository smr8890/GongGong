import datetime
from unittest import TestCase

from xtu_ems.ems.model import CourseInfo
from xtu_ems.util.icalendar import BaseCalendar
from xtu_ems.util.ics_util import CourseIcalendarUtil


class TestCourseIcalendarUtil(TestCase):
    """测试ics工具"""

    def test_convert_course_to_event(self):
        """测试课程转化为事件"""
        course = CourseInfo(
            name="网络安全协议分析",
            teacher="周维副教授",
            classroom="北山二阶梯",
            weeks="2-6,8-14",
            start_time=5,
            duration=2,
            day="Monday",
        )
        util = CourseIcalendarUtil()
        events = util.convert_course_to_event(course, datetime.date(year=2024, month=8, day=26))
        calendar = BaseCalendar()
        for event in events:
            calendar.add_event(event)
        ics = calendar.to_ical()
        self.assertIsNotNone(ics)
        print(ics)
