FROM python:3.10-slim

# 1. System Dependencies (Cached Layer)
# Installed once and cached.
RUN apt-get update && apt-get install -y \
    wget gnupg ffmpeg curl chromium \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
WORKDIR /app

# 2. Dependency Installation (Cached Layer)
# We copy ONLY the dependency files first.
# This ensures that these layers are reused unless requirements/package.json changes.
COPY backend/requirements.txt ./backend/
COPY frontend/package*.json ./frontend/

# Install Backend Deps
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Install Frontend Deps
WORKDIR /app/frontend
RUN npm install

# 3. Source Code & Build (Invalidates when source changes)
# Copy Frontend source and build
COPY frontend ./
RUN npm run build
RUN npx remotion bundle src/remotion/index.ts dist-bundle

# Copy Backend source (Last layer for fastest iteration on Python code)
WORKDIR /app/backend
COPY backend ./

# 4. Runtime
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
