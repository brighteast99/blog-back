# syntax=docker/dockerfile:1.7-labs

FROM python:3.11-slim
LABEL maintainer="Donghwan Kim <brighteast99@gmail.com>"
LABEL description="Python server for Donghwan's blog"

WORKDIR /app
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install -r /tmp/requirements.txt

COPY --exclude=requirements.txt . .

ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
RUN python3 manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
