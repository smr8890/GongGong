# 基础镜像
FROM python:3.11-slim-bullseye AS base

LABEL authors="leo"

# 设置工作目录
WORKDIR /app

ARG PROXY="https://mirrors.cloud.tencent.com/pypi/simple"

# 安装依赖，仅在 requirements 文件发生变化时重新安装
COPY ./requirements*.txt ./
RUN pip install --upgrade pip -i $PROXY \
    && pip config set global.index-url $PROXY \
    && pip install -r requirements.txt \
    && rm -f requirements*.txt

# 应用构建阶段
FROM base

LABEL authors="leo"


# 复制源码文件
COPY ./src /app


# 创建日志目录
RUN mkdir /logs

# 暴露端口
EXPOSE 8000

# 入口命令
ENTRYPOINT ["python", "app.py"]
