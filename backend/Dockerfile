FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini ./
COPY alembic ./alembic
COPY start.sh ./
COPY start-staging.sh ./
COPY app ./app
COPY tests/fixtures/official ./tests/fixtures/official
EXPOSE 8000
CMD ["sh", "start.sh"]
