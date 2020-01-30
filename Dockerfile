FROM python:3.8.1-alpine3.11

COPY ./requirements.txt /requirements.txt

RUN pip install --upgrade pip
RUN apk add --no-cache --virtual .build-deps gcc musl-dev curl && \
    pip install -r /requirements.txt && \
    apk del .build-deps


WORKDIR /app

COPY ./src/rickbot .

EXPOSE 3000

CMD python app.py