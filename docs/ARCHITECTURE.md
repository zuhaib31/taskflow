# Architecture

## Overview

TaskFlow is a containerized two-tier web application deployed on AWS EC2 with a fully automated CI/CD pipeline. The system separates the application code, infrastructure, and delivery automation into distinct, independently versioned layers.

## High-Level Diagram
+-----------------+     git push      +----------------+
|   Developer     | ----------------> |   GitHub repo  |
|   (VS Code)     |                   +--------+-------+
+-----------------+                            |
| SCM polling (every 5 min)
v
+------------------+-----------------+
|          AWS EC2 (t2.micro)       |
|                                    |
|   +-----------------------------+  |
|   |  Jenkins (custom image)     |  |
|   |  - Polls GitHub             |  |
|   |  - Runs pipeline            |  |
|   |  - Talks to Docker daemon   |  |
|   +-------------+---------------+  |
|                 | docker compose   |
|                 v                  |
|   +-----------------------------+  |
|   |   taskflow-web (Flask)      |  |
|   |   port 5000                 |  |
|   +-------------+---------------+  |
|                 |                  |
|                 v                  |
|   +-----------------------------+  |
|   |   taskflow-mysql (MySQL 8)  |  |
|   |   port 3306 (internal only) |  |
|   +-----------------------------+  |
+------------------+-----------------+
|
| http://<public-ip>:5000
v
+----+----+
|  User   |
| browser |
+---------+

## Components

### Application Layer

**Flask web application** serving a task and project management system.

- Python 3.11 on Gunicorn (production WSGI server)
- Session-based authentication with Werkzeug password hashing
- Direct SQL access via `flask-mysqldb` (no ORM by design - keeps it close to the original two-tier pattern)
- Application factory pattern for testability
- Blueprints for modular routing (main, auth, projects, tasks)
- Custom 404 error handling

### Data Layer

**MySQL 8.0** running in a dedicated container.

- Four tables: users, projects, tasks, comments
- Foreign key constraints with ON DELETE CASCADE
- Indexed columns for common query patterns
- Persistent storage via named Docker volume (`mysql_data`)
- Schema migrations auto-applied on first boot via `docker-entrypoint-initdb.d` mount

See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for the full schema.

### Container Orchestration

**Docker Compose** defines a two-service stack with a private bridge network.

- `web` and `mysql` services share an isolated `taskflow-network`
- `depends_on: service_healthy` ensures Flask only starts after MySQL passes its health check
- Health checks defined on both services for orchestration safety
- Restart policy `unless-stopped` for resilience across host reboots
- All sensitive values injected from `.env` at runtime (never baked into images)

### CI/CD Layer

**Jenkins** running as a containerized service on the same EC2 instance.

- Custom Jenkins image (`taskflow-jenkins:latest`) with Docker CLI and Compose pre-installed
- Docker-out-of-Docker pattern: Jenkins mounts the host's Docker socket to orchestrate sibling containers
- SCM polling every 5 minutes (chosen over webhooks because the EC2 public IP changes between sessions)
- Pipeline defined as code in `Jenkinsfile` (committed to the repo)

### Infrastructure Layer

**AWS EC2** single-instance deployment.

- `t2.micro` instance running Ubuntu 24.04 LTS
- 20 GB EBS volume
- 2 GB swap file configured to handle memory pressure on the 1 GB RAM instance
- Security group restricting access:
  - Port 22 (SSH) from operator's IP only
  - Port 8080 (Jenkins) accessed via SSH tunnel, not exposed publicly
  - Port 5000 (application) open to the internet
- Single AWS region: ca-central-1 (Canada Central)

## Pipeline Stages

The Jenkins pipeline runs six stages in strict order. Failure at any stage stops the pipeline.

1. **Checkout** - Pull latest code from GitHub into Jenkins workspace
2. **Sync to Deploy Directory** - Update the host's working directory (`/home/ubuntu/taskflow`) to match origin/main
3. **Test** - Run 40 pytest tests in an ephemeral `python:3.11-slim` container
4. **Build** - Build the Flask Docker image with layer caching
5. **Deploy** - Recreate the application container via `docker compose up -d`
6. **Health Check** - Poll the container's Docker health status until `healthy` (up to 60 seconds)

## Design Decisions

### Why Docker-out-of-Docker instead of Docker-in-Docker?

Mounting the host's Docker socket into Jenkins lets it create sibling containers on the host. Alternative (Docker-in-Docker, nested) is heavier, slower, and introduces compatibility issues. The trade-off: Jenkins has root-equivalent control of the host's Docker daemon, which is acceptable for a single-instance portfolio project but would need stricter isolation in a real multi-tenant environment.

### Why a custom Jenkins image?

The official `jenkins/jenkins:lts-jdk17` image does not include the Docker CLI. Installing the CLI manually inside a running container is lost when the container is recreated. Building a custom image with `docker` and `docker compose` baked in makes the CI environment reproducible and survives container recreation.

### Why SCM polling instead of GitHub webhooks?

Webhooks require Jenkins to be reachable at a stable URL. The EC2 instance is stopped during inactive periods and receives a new public IP on each start. Polling avoids this constraint at the cost of up to 5 minutes of latency between push and build trigger.

### Why ephemeral test containers?

Running tests inside Jenkins would mix concerns (Jenkins is an orchestrator, not a Python runtime) and bloat the Jenkins image. Spinning up a fresh `python:3.11-slim` container per build keeps the test environment isolated, reproducible, and version-pinned to match production.

### Why separate `requirements-test.txt`?

Production requirements include `flask-mysqldb`, which requires MySQL client libraries to compile. Tests do not need a real database connection (the validator tests are pure functions, and route tests mock the MySQL driver entirely). A leaner test requirements file makes the test environment portable to any machine, including local development on macOS without MySQL installed.

### Why swap space on the instance?

Running Jenkins (Java, memory-hungry), MySQL, and Flask on a 1 GB RAM `t2.micro` is genuinely tight. A 2 GB swap file provides overflow capacity that prevents the OOM killer from terminating containers under load. The trade-off (slower performance when swap is hit) is acceptable for a portfolio project and avoids paying for a larger instance.

## Limitations and Future Improvements

- **No HTTPS.** Application is served over plain HTTP. Adding Nginx as a reverse proxy with Let's Encrypt certificates would be the standard production fix.
- **No external secrets management.** Secrets live in a `.env` file on the host. A production system would use AWS Secrets Manager or HashiCorp Vault.
- **Single instance, no horizontal scaling.** Acceptable for portfolio; production would use an autoscaling group behind a load balancer.
- **No application-level monitoring.** Container health checks exist, but there is no Prometheus, Grafana, or log aggregation.
- **No infrastructure as code.** EC2 was provisioned via the AWS console. Terraform or CloudFormation would make the infrastructure reproducible.
- **No database backups.** The MySQL volume is persistent but not backed up. A production system would snapshot the EBS volume or stream backups to S3.
