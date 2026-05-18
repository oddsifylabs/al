# Jed Hermes Manager Poller
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY jed-poller.py .
RUN pip install --no-cache-dir requests

ENV DASHBOARD_URL=http://al-dashboard:8080
ENV POLL_INTERVAL=30

CMD ["python", "jed-poller.py"]
