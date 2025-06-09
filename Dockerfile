# Stage 1: Base stage for common setup
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONDONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONPATH=/app \
    PATH="/home/appuser/.local/bin:$PATH"

# Create and switch to a non-root user
RUN useradd --create-home appuser
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pip and pip-tools
RUN pip install --upgrade pip pip-tools

# Copy requirements files
COPY requirements.in requirements.txt ./

# Generate requirements.txt if it doesn't exist
RUN if [ ! -f requirements.txt ]; then pip-compile requirements.in; fi

# Stage 2: Development stage (can be used for local development)
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Stage 3: Production stage
FROM base as production

# Install only runtime dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Collect static files (uncomment if needed)
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "django_project.wsgi:application", "--bind", "0.0.0.0:8000"]
