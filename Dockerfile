
FROM python:3.10-alpine3.16
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirements.txt /requirements.txt
COPY . /code
COPY ./scripts /scripts
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base postgresql-dev musl-dev linux-headers && \
    /py/bin/pip install -r /requirements.txt && \
    apk del .tmp-deps && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R app:app /vol && \
    chown -R app:app /code && \
    chmod -R 755 /vol && \
    chmod -R 755 /code && \
    chmod -R +x /scripts



ENV PATH="/scripts:/py/bin:$PATH"

USER app

CMD ["run.sh"]