# Welcome to the Bhread code repository

[Bhread website](https://bhread.com)

## Code

We follow most of [HackSoftware/Django-Styleguide](https://github.com/HackSoftware/Django-Styleguide)
This means that we try to have thin models, no signals (there's an exception), selectors, services

For reactivity, [htmx](https://htmx.org) is used.

For styling, Bhread uses [Water.css](https://watercss.kognise.dev/) for its base style and extends it with inline styles

The [bhread diagram](./bhread.drawio) contains an ERD, and some flow diagrams.
Threads are stored in an adjanency list structure

## Running

Run redis docker image:
docker run -p 6379:6379 -it redis/redis-stack:latest

Run django-q
poetry run manage.py qcluster

Run tailwind:
poetry run manage.py tailwind start

Run django:
poetry run manage.py runserver


## Contribute

Improvements in code or art submissions (see art/memes) are welcome!
Simply fork this repo, and make a pull request.
