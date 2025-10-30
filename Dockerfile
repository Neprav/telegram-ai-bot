FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Environment variable for port
ENV PORT=8080

# Expose port 8080 (optional for Cloud Run, but useful for local testing)
EXPOSE 8080

# Start the application
CMD ["gunicorn", "-w", "1", "-k", "gevent", "-b", "0.0.0.0:8080", "--timeout", "60", "main:app"]
