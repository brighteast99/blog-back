#
# Python server for blog backend
#
# build:
#   docker build --force-rm -t brighteast99/blog-server:<version> .

FROM python:3.10-slim
LABEL maintainer="Donghwan Kim <brighteast99@gmail.com>"
LABEL description="Python server for Donghwan's blog"

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["/bin/bash", "-c", "echo yes | python3 manage.py collectstatic && python3 manage.py runserver 0.0.0.0:8000"]

