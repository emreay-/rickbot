FROM python:3.8.1-alpine3.11

RUN pip install --upgrade pip
RUN apk add --no-cache --virtual .build-deps gcc musl-dev curl 

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /app
COPY ./src/rickbot .

# CMD python app.py