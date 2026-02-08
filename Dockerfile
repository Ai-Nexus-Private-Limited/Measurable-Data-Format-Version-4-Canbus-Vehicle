# ---------- BASE IMAGE ----------
FROM python:3.10-slim

# ---------- SYSTEM DEPENDENCIES ----------
# Needed for:
# - asammdf (lz4, numpy)
# - parquet (pyarrow)
# - cantools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    liblz4-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------- WORKDIR ----------
WORKDIR /app

# ---------- PYTHON DEPENDENCIES ----------
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------- COPY APP ----------
COPY decoder.py .

# ---------- ENV ----------
ENV PYTHONUNBUFFERED=1

# ---------- ENTRYPOINT ----------
CMD ["python", "decoder.py"]
