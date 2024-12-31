from datetime import timedelta

from pydantic_settings import BaseSettings


class CacheConfig(BaseSettings):
    """缓存配置"""

    DEFAULT_SUBMIT: timedelta = timedelta(minutes=1)
    """默认提交时间间隔"""

    PERSONAL_INFO_UPDATE: timedelta = timedelta(days=10)
    """个人信息更新时间间隔"""
    PERSONAL_INFO_SUBMIT: timedelta = DEFAULT_SUBMIT
    """个人信息提交时间间隔"""

    SCORE_UPDATE: timedelta = timedelta(days=1)
    """主修成绩更新时间间隔"""
    SCORE_SUBMIT: timedelta = DEFAULT_SUBMIT
    """主修成绩提交时间间隔"""

    MINOR_SCORE_UPDATE: timedelta = timedelta(days=1)
    """辅修成绩更新时间间隔"""
    MINOR_SCORE_SUBMIT: timedelta = DEFAULT_SUBMIT
    """辅修成绩提交时间间隔"""

    COURSE_UPDATE: timedelta = timedelta(days=1)
    """课表更新时间间隔"""
    COURSE_SUBMIT: timedelta = DEFAULT_SUBMIT
    """课表提交时间间隔"""

    EXAM_UPDATE: timedelta = timedelta(days=2)
    """考试更新时间间隔"""
    EXAM_SUBMIT: timedelta = DEFAULT_SUBMIT
    """考试提交时间间隔"""

    RANK_UPDATE: timedelta = timedelta(days=1)
    """排名更新时间间隔"""
    RANK_SUBMIT: timedelta = DEFAULT_SUBMIT
    """排名提交时间间隔"""

    CALENDAR_UPDATE: timedelta = timedelta(days=1)
    """校历更新时间间隔"""
    CALENDAR_SUBMIT: timedelta = DEFAULT_SUBMIT
    """校历提交时间间隔"""

    TODAY_CLASSROOM_UPDATE: timedelta = timedelta(hours=1)
    """今天教室更新时间间隔"""
    TODAY_CLASSROOM_SUBMIT: timedelta = DEFAULT_SUBMIT
    """今日教室提交时间间隔"""

    TOMORROW_CLASSROOM_UPDATE: timedelta = timedelta(hours=1)
    """明天教室更新时间间隔"""
    TOMORROW_CLASSROOM_SUBMIT: timedelta = DEFAULT_SUBMIT
    """明天教室提交时间间隔"""


CACHE_CONFIG = CacheConfig()
