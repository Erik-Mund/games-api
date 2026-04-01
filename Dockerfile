FROM python:3.11-slim

# Prevent Python from buffering logs
ENV PYTHONBUFFERED=1

WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Render uses 10000)
EXPOSE 10000

# Start app
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:10000"]