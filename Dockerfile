# Gunakan image Python yang ringan
FROM python:3.12-slim

# Install library sistem yang dibutuhkan oleh OpenCV dan lainnya
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory di container
WORKDIR /app

# Copy semua file project ke dalam container
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Jalankan aplikasi Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
