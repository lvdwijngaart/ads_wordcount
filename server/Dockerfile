FROM python:3.12-slim

# System deps (none strictly required here, but keep it minimal)
RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# 0.0.0.0 so it’s reachable from outside the container
EXPOSE 18861

CMD ["python", "server.py"]
