FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY req2.txt .
RUN pip install --no-cache-dir -r req2.txt

COPY req3.txt .
RUN pip install --no-cache-dir -r req3.txt

COPY ./src ./src
COPY --from=common . ./common

ENTRYPOINT [ "python", "-m", "src", "--mock" ]
