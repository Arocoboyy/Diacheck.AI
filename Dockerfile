# Gunakan image python ringan
FROM python:3.10-slim

# Non-interaktif
ENV DEBIAN_FRONTEND=noninteractive

# Set working dir
WORKDIR /app

# Install dependency sistem minimum
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirement dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project
COPY . .

# Ekspos port
EXPOSE 5005

# Jalankan Flask
CMD ["python", "app.py"]
