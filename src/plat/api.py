from fastapi import APIRouter, Body, Header
from fastapi import Response
from fastapi.params import Param
from pydantic import BaseModel

from plat.service import account_service, course_service, info_service, score_service, exam_service, rank_service, \
    today_classroom_service, tomorrow_classroom_service, calendar_service, minor_score_service
from plat.service.acc_service import ExpiredAccountException, BannedAccountException
from plat.service.entity import Account
from plat.service.info_service import IService
from xtu_ems.ems.ems import InvalidAccountException, InvalidCaptchaException, UninitializedPasswordException
from xtu_ems.ems.model import TeachingCalendar, CourseList, ExamInfoList
from xtu_ems.util.icalendar import BaseCalendar
from xtu_ems.util.ics_util import CourseIcalendarUtil, ExamIcalendarUtil

app = APIRouter()
ics_utils = {
    "Course": CourseIcalendarUtil(),
    "Exam": ExamIcalendarUtil()
}


class CommonResponse(BaseModel):
    code: int
    message: str
    data: object


def success(data=None, message='success'):
    return CommonResponse(
        code=1,
        message=message,
        data=data
    )


def fail(data=None, message='fail'):
    return CommonResponse(
        code=0,
        message=message,
        data=data
    )


def invalid_authority():
    return CommonResponse(
        code=-1,
        message='无效的权限',
        data=None
    )


@app.post("/login")
async def login(username: str = Body(description="学号"), password: str = Body(description="密码")):
    """登陆接口"""
    try:
        account = await account_service.login(username, password)
        if account:
            return success({'token': account.token})
        else:
            return fail()
    except ExpiredAccountException as e:
        return fail(message=f"账户 {e.username} 已过期")
    except BannedAccountException as e:
        return fail(message=f"账户 {e.username} 已被封禁")
    except InvalidAccountException as e:
        return fail(message=f"账户密码错误")
    except InvalidCaptchaException as e:
        return fail(message=f"系统繁忙，请稍后重试")
    except UninitializedPasswordException as e:
        return fail(message=f"账户需要修改密码")
    except TimeoutError as e:
        return fail(message=f'服务器超时，请稍后')


async def do_gets(service: IService[any], token: str):
    """获取信息"""
    try:
        account: Account = await account_service.auth_with_token(token)
    except ExpiredAccountException as e:
        return fail(message=f"账户 {e.username} 已过期")
    if account and account.token == token:
        data = await service.get_info(account.student_id)
        return success(data)
    else:
        return invalid_authority()


@app.get("/courses")
async def get_courses(token: str = Header(description="用户凭证")):
    """获取课表"""
    info = await do_gets(course_service, token)
    return info


@app.get("/info")
async def get_info(token: str = Header(description="用户凭证")):
    """获取用户信息"""
    return await do_gets(info_service, token)


@app.get("/scores")
async def get_score(token: str = Header(description="用户凭证")):
    """获取成绩"""
    return await do_gets(score_service, token)


@app.get("/minor/scores")
async def get_score_by_term(token: str = Header(description="用户凭证")):
    """获取指定学期成绩"""
    return await do_gets(minor_score_service, token)


@app.get("/exams")
async def get_exam(token: str = Header(description="用户凭证")):
    """获取考试"""
    return await do_gets(exam_service, token)


@app.get("/rank")
async def get_rank(token: str = Header(description="用户凭证")):
    """获取排名"""

    return await do_gets(rank_service, token)


@app.get("/classroom/today")
async def get_today_classroom(token: str = Header(description="用户凭证")):
    """获取今天教室"""
    return await do_gets(today_classroom_service, token)


@app.get("/classroom/tomorrow")
async def get_tomorrow_classroom(token: str = Header(description="用户凭证")):
    """获取明天教室"""
    return await do_gets(tomorrow_classroom_service, token)


@app.get("/calendar")
async def get_calendar(token: str = Header(description="用户凭证")):
    """获取校历"""
    return await do_gets(calendar_service, token)


@app.get("/courses.ics")
async def get_courses_ics(token: str = Param(description="用户凭证")):
    """获取课表ics"""
    teaching_calendar = (await do_gets(calendar_service, token)).data
    if not teaching_calendar or not isinstance(teaching_calendar, TeachingCalendar):
        return fail(message="获取校历失败")
    base_date = teaching_calendar.start
    courses = (await do_gets(course_service, token)).data
    if not courses or not isinstance(courses, CourseList):
        return fail(message="获取课表失败")
    events = ics_utils["Course"].convert_courses_to_events(courses.courses, base_date)
    calendar = BaseCalendar()
    calendar.events = events
    ics = calendar.to_ical()
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=courses.ics"
        }
    )


@app.get("/exams.ics")
async def get_exams_ics(token: str = Param(description="用户凭证")):
    """获取考试ics"""
    exams = (await do_gets(exam_service, token)).data
    if not exams or not isinstance(exams, ExamInfoList):
        return fail(message="获取考试失败")
    events = ics_utils["Exam"].convert_exams_to_events(exams)
    calendar = BaseCalendar()
    calendar.events = events
    ics = calendar.to_ical()
    return Response(
        content=ics,
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=exams.ics"
        }
    )
