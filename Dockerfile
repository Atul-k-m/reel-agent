FROM python:3.10-slim

# Install System Deps for Remotion (Chromium, FFmpeg, Node.js)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ffmpeg \
    curl \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Environment for Remotion to use installed Chromium
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

WORKDIR /app

# --- FRONTEND BUILD ---
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install

COPY frontend ./
RUN npm run build
# Pre-bundle Remotion to save runtime CPU
RUN npx remotion bundle src/remotion/index.ts dist-bundle

# --- BACKEND SETUP ---
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./

# --- RUN ---
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
