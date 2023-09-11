FROM node:18-buster-slim as node_base

# The builder image, used to build the virtual environment
FROM python:3.11-buster as builder
ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME=/etc/poetry

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

ENV PATH="$POETRY_HOME/bin:$PATH"
# RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim-buster as runtime

WORKDIR /code

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

COPY --from=node_base / /
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# COPY . /code/
