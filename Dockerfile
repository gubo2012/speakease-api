# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install curl for health check
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PORT=8010
ENV PYTHONPATH=/app
ENV K_SERVICE=true
ENV GOOGLE_APPLICATION_CREDENTIALS=gcpxmlb25-e063bdf91528.json

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Copy the rest of the application
COPY . .

# Change ownership of the application files
RUN chown -R appuser:appuser /app

# List all files in the /app directory and show current directory
RUN ls -a

RUN pwd

RUN ls -a /app/app

# Expose the port the app runs on
EXPOSE 8010

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8010/ || exit 1

# Switch to non-root user
USER appuser

# Command to run the application with proper logging
CMD ["/bin/bash", "-c", "cd /app && uvicorn app.main:app --host 0.0.0.0 --port 8010 --log-level info"] 