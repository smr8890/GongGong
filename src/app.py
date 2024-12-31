import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from plat.api import app
from plat.backgroud_task import session_refresher_in_background

env = os.environ.get('ENV', 'dev')
if env == 'prod':
    fastapi_app = FastAPI(lifespan=session_refresher_in_background, docs_url=None, redoc_url=None, openapi_url=None)
else:
    fastapi_app = FastAPI(lifespan=session_refresher_in_background)
fastapi_app.include_router(app)
fastapi_app.mount('/icalendar', StaticFiles(directory='static'), name="icalendar")

os.makedirs('../logs', exist_ok=True)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(fastapi_app, port=8000, host='0.0.0.0', log_config='./log_config.json')
