FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN echo "force-rebuild-2026-05-13"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --force-reinstall

COPY . .

EXPOSE 10000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:$PORT", "GameBaseAPI.run:app"]