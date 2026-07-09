FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 user
COPY --chown=user backend/ ./backend/
USER user

ENV HOST=0.0.0.0
ENV PORT=7860
EXPOSE 7860

WORKDIR /app/backend
CMD ["python", "main.py"]
