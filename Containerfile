FROM python:3.12.2-alpine3.19 as requirements-stage
ENV PYTHONUNBUFFERED=1

WORKDIR /tmp

# For ARM builds where some wheels might be unavailable
RUN apk --no-cache add gcc musl-dev libffi-dev

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12.2-alpine3.19
ENV PYTHONUNBUFFERED=1

WORKDIR /app
RUN apk --no-cache add gcc musl-dev libffi-dev
COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --no-cache-dir --upgrade gunicorn
COPY . /app
RUN apk del gcc musl-dev libffi-dev

WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "8", "app:app"]
