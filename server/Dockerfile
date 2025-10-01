FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./data ./data
COPY --from=common . ./common

HEALTHCHECK --interval=1m --timeout=10s --retries=3 --start-period=2s \
    CMD python -c "import rpyc; rpyc.connect(\"0.0.0.0\", ${RPYC_PORT})"
ENTRYPOINT [ "python", "-m", "src" ]
