FROM python:3.12-slim

ENV REQUIREMENTS="requirements.txt"
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=common . common

ENTRYPOINT [ "python", "-m", "src", "--mock" ]
