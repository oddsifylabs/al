# Hermes Agent Railway Deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Hermes Agent (mounted from host or cloned)
# For Railway: clone the Hermes Agent repo
RUN git clone https://github.com/NousResearch/hermes-agent.git /hermes-agent
WORKDIR /hermes-agent

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Set environment
ENV HERMES_HOME=/hermes
ENV PYTHONUNBUFFERED=1

# Expose port for webhook
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run gateway in webhook mode
CMD ["python", "-m", "hermes_cli.main", "gateway", "run", "--replace"]
