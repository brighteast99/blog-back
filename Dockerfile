FROM python:3.11-alpine

WORKDIR /app

RUN --mount=type=bind,src=requirements.txt,target=requirements.txt \
    pip install -r requirements.txt

COPY gunicorn-conf.py /conf/gunicorn-conf.py
COPY manage.py manage.py
COPY blog blog

ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
RUN python3 manage.py collectstatic --noinput

CMD ["gunicorn", "blog.wsgi:application", "--config", "/conf/gunicorn-conf.py"]