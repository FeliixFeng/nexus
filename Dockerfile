FROM python:3.11-slim

WORKDIR /app

# 安装uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装依赖
RUN uv sync --frozen --no-dev

# 复制项目代码
COPY . .

# 收集静态文件
RUN uv run python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
