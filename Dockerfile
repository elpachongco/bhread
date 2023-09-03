# syntax=docker/dockerfile:1
FROM python:3.11.5-slim as python-base
WORKDIR /
ENV POETRY_VERSION=1.6.1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

RUN curl -sSL https://install.python-poetry.org | python3 -
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
COPY . .
RUN $POETRY_HOME/bin/poetry install --only main
EXPOSE 8000
CMD ["poetry", "run", "python3", "manage.py", "runserver", "0.0.0.0:8000"]
