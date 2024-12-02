from fastapi import APIRouter, Body, Header
from pydantic import BaseModel

from plat.service import account_service, course_service, info_service, score_service, exam_service, rank_service, \
    today_classroom_service, tomorrow_classroom_service, calendar_service
from plat.service.acc_service import ExpiredAccountException, BannedAccountException
from plat.service.entity import Account
from plat.service.info_service import IService
from xtu_ems.ems.ems import InvalidAccountException, InvalidCaptchaException

app = APIRouter()


class Response(BaseModel):
    code: int
    message: str
    data: object


def success(data=None, message='success'):
    return Response(
        code=1,
        message=message,
        data=data
    )


def fail(data=None, message='fail'):
    return Response(
        code=0,
        message=message,
        data=data
    )


def invalid_authority():
    return Response(
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
