FROM python:3.11-slim-bullseye
LABEL authors="leo"

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
COPY ./requirements.ems.txt ./requirements.ems.txt

RUN pip install --upgrade pip -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN pip install -r requirements.txt

COPY ./src /app

EXPOSE 8000
ENTRYPOINT ["python", "app.py"]
