FROM python:3.12-slim

WORKDIR /app

# Prevent Python from writing pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies rapidly avoiding cache bloat
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files securely
COPY . .

# Ensure data directory boundaries exist
RUN mkdir -p /app/data

# Ensure smart bootstrapper is executable
RUN chmod +x docker-entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]
