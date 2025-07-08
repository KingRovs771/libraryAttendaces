# ------------------------------------------
# Stage 1: Backend Setup with Python
# ------------------------------------------
FROM python:3.9-slim AS backend

WORKDIR /app/backend

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# ------------------------------------------
# Stage 2: Frontend Setup with Node.js
# ------------------------------------------
FROM node:16 AS frontend

WORKDIR /app/frontend

# Install frontend dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source
COPY frontend/ .

# Build frontend assets
RUN npm run build

# ------------------------------------------
# Final Stage: Combine Everything
# ------------------------------------------
FROM python:3.9-slim

WORKDIR /app

# Copy backend app
COPY --from=backend /app/backend ./backend

# Copy built frontend
COPY --from=frontend /app/frontend/build ./frontend/build

# Expose backend port
EXPOSE 8000

# Run backend app (update with actual entrypoint if needed)
CMD ["python", "backend/app.py"]