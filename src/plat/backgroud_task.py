import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_settings import BaseSettings

from plat.service import account_service


class RefreshConfiguration(BaseSettings):
    """后台任务配置"""
    REFRESH_INTERVAL: int = 2 * 60  # 2min


RefreshConfig = RefreshConfiguration()

background_task = []


@asynccontextmanager
async def session_refresher_in_background(app: FastAPI):
    """后台任务，用于刷新session, 返回任务对象"""
    task = asyncio.create_task(account_service.refresh_session(RefreshConfig.REFRESH_INTERVAL))
    background_task.append(task)
    yield
