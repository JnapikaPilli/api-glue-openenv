# ── Stage 1: Build React Frontend ──────────────────────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Final Python Server ──────────────────────────────────────────
FROM python:3.11-slim

LABEL name="virtual-ops-manager" \
      version="1.1.0" \
      description="Research-grade OpenEnv for Virtual Operations Management" \
      author="Jnapika Pilli"

# ── System deps ───────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies ───────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy Server Logic ─────────────────────────────────────────────────────
COPY server/ ./server/
COPY inference.py .
COPY openenv.yaml .
COPY pyproject.toml .
COPY README.md .
COPY .env* ./

# ── Copy Built Frontend from Stage 1 ──────────────────────────────────────
COPY --from=frontend-builder /build/frontend/dist ./frontend/dist

# ── Environment variables ─────────────────────────────────────────────────
ENV API_BASE_URL="https://api.groq.com/openai/v1" \
    MODEL_NAME="llama-3.1-8b-instant" \
    PORT=7860 \
    PYTHONPATH=/app

EXPOSE 7860

# ── Health check (Points to core API) ─────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/api/state || exit 1

# ── Start server (The Validated #8 Pattern) ───────────────────────────────────
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
