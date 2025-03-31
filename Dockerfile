# ============================
# Stage 1: Build Environment
# ============================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/requirements.txt

# Create a virtual environment and install dependencies
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install -r requirements.txt

# ============================
# Stage 2: Runtime Environment
# ============================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy application source code to container
COPY . /app

# Copy virtual environment from builder stage
COPY --from=builder /app/venv /app/venv

# Set PATH to include venv binaries
ENV PATH="/app/venv/bin:$PATH"

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
