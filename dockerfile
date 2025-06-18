FROM python:3.11-slim

# Tambahkan dependensi sistem untuk mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Buat folder kerja
WORKDIR /app

# Salin requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file project ke container
COPY . .

# Jalankan server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
