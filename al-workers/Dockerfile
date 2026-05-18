# AL Worker Poller Template
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY worker-poller.py .
RUN pip install --no-cache-dir requests

# WORKER_ID must be set at deploy time: ruth, ms-anderson, octavia, mitch, malcom
ENV DASHBOARD_URL=http://al-dashboard:8080
ENV POLL_INTERVAL=30

CMD ["python", "worker-poller.py"]
