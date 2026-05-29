# ==============================================================================
# TaskFlow Dockerfile
#
# Builds a container image for the Flask application. Uses a slim Python base
# to keep the image small, installs only what's needed, runs as a non-root
# user for security, and serves via Gunicorn (a production WSGI server).
# ==============================================================================

# Use a specific, slim Python version. Pinning the version (not "latest")
# ensures reproducible builds - the image is the same every time.
FROM python:3.11-slim

# Set environment variables for Python behavior:
# - PYTHONDONTWRITEBYTECODE: don't write .pyc files (cleaner container)
# - PYTHONUNBUFFERED: send logs straight to terminal (so we see them in real time)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container. All following commands
# run from here, and our code lives here.
WORKDIR /app

# Install system dependencies needed to build the MySQL client library.
# flask-mysqldb needs these to compile. We clean up apt cache afterward
# to keep the image small (combining into one RUN layer also helps).
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY requirements.txt first, then install dependencies.
# This is a Docker layer-caching optimization: if our code changes but
# requirements don't, Docker reuses the cached dependency layer instead
# of reinstalling everything. Big speedup on rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code.
COPY . .

# Create a non-root user and switch to it. Running as root inside a
# container is a security risk - if someone breaks out of the app, they'd
# have root. Running as an unprivileged user limits the damage.
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Document that the container listens on port 5000. This is informational
# (doesn't actually publish the port - that's done in docker-compose).
EXPOSE 5000

# Health check: Docker periodically runs this to know if the container is
# healthy. It hits our /health endpoint. If it fails repeatedly, Docker
# marks the container unhealthy (useful for orchestration and monitoring).
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start the app with Gunicorn (production WSGI server) instead of Flask's
# built-in dev server. Gunicorn handles multiple concurrent requests properly.
# - "run:app" means: in run.py, use the variable named "app"
# - 3 workers is a reasonable default for a small instance
# - bind to 0.0.0.0 so it's reachable from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]
