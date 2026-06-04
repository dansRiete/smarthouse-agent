FROM python:3.11-slim

WORKDIR /app

# Run as non-root user for strict security
RUN groupadd -r agentgroup && useradd -r -g agentgroup agentuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Create directory for SQLite DB and ensure permissions
RUN mkdir -p /app/data && chown -R agentuser:agentgroup /app

USER agentuser

ENV PYTHONPATH=/app/src
CMD ["python", "src/main.py"]
