# AIIA-NTBLM-Factory — Production image
FROM python:3.11-slim

# System deps: ffmpeg for video, fonts for PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Pin setuptools<69 to keep google-api-python-client==1.12.3 importable
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Credentials are injected at runtime via env (never baked into image)
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python", "factory.py"]
CMD ["--help"]
