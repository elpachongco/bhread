# Welcome to the Bhread code repository

[Bhread website](https://bhread.com)

## Code

We follow most of [HackSoftware/Django-Styleguide](https://github.com/HackSoftware/Django-Styleguide)
This means that we try to have thin models, no signals (there's an exception), selectors, services

For backend and frontend connectivity, [htmx](https://htmx.org) is used.

For styling, Bhread uses [Tailwind]() and is heavily inspired (literal copy) by
[Water.css](https://watercss.kognise.dev/) style.

NOTE: By default, [Slippers]() are loaded to every template.

For client scripting, alpine.js is used.

The [bhread diagram](./bhread.drawio) contains an ERD, and some flow diagrams.
Threads are stored in a tree structure.

## Running the program

The recommended way of development is to use docker.

These are the steps for development without docker:

Install pre-commit in a new repo:

```sh
poetry run pre-commit install
```
or Run pre-commit in a new repo:
```sh
poetry run pre-commit run --all-files
```

Run redis docker image:

```sh
docker run -p 6379:6379 -it redis/redis-stack:latest
```

Run django-q
```sh
poetry run manage.py qcluster
```

Run tailwind:
```sh
poetry run manage.py tailwind start
```

Run django:
```sh
poetry run manage.py runserver
```

Run Dockerfile:
```sh
docker build -t testing-bhread .
docker run -p 127.0.0.1:8000:8000 testing-bhread
```

Run docker compose:
```sh
docker compose up --build or
```
```sh
docker compose up
```

## Contribute

Improvements in code or art submissions (see art/memes) are welcome!
Simply fork this repo, and make a pull request.
