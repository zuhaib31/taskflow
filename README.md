# TaskFlow

A task and project management web application built with Flask and MySQL, containerized with Docker, deployed on AWS EC2, and delivered through a Jenkins CI/CD pipeline with automated testing.

## What This Project Demonstrates

This is a DevOps portfolio project. The focus is on the deployment lifecycle around a web application rather than on the application's product features.

- **Containerization** - Multi-container application orchestrated with Docker Compose
- **CI/CD** - Six-stage Jenkins pipeline: Checkout → Sync → Test → Build → Deploy → Health Check
- **Automated testing** - 40 pytest tests gating every deployment
- **Cloud deployment** - AWS EC2 with security group network isolation
- **Custom images** - A purpose-built Jenkins Docker image for reproducible CI
- **Infrastructure debugging** - Real problems solved: Docker socket permissions, container networking, SSH tunneling, git history correction

## Tech Stack

| Layer | Technology |
|-------|------------|
| Application | Flask 3.0, Python 3.11, Gunicorn |
| Database | MySQL 8.0 |
| Containers | Docker, Docker Compose |
| CI/CD | Jenkins (custom image with Docker CLI baked in) |
| Testing | pytest |
| Cloud | AWS EC2 (t2.micro, Ubuntu 24.04) |
| Frontend | HTML/CSS (no JS framework - kept minimal) |

## Architecture at a Glance
Developer push → GitHub → Jenkins (SCM polling)
→ Run 40 pytest tests
→ Build Docker image
→ Deploy via docker compose
→ Verify container health
→ Live app at http://<ec2-ip>:5000
For the full architecture explanation and design decisions, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Pipeline Screenshots

The CI/CD pipeline is the centerpiece of this project. Key visuals:

- All six pipeline stages passing across multiple builds: `screenshots/04-cicd-pipeline/pipeline-stage-view-all-green.png`
- 40 tests passing inside the pipeline: `screenshots/04-cicd-pipeline/pipeline-console-test-stage.png`
- Pipeline auto-triggered by a git push: `screenshots/04-cicd-pipeline/pipeline-scm-change.png`
- Successful end-to-end run: `screenshots/04-cicd-pipeline/pipeline-console-success.png`

## Application Screenshots

- Landing page: `screenshots/02-app-live/app-landing-page.png`
- Dashboard with stats: `screenshots/02-app-live/app-dashboard-with-data.png`
- Kanban board: `screenshots/02-app-live/app-multiple-tasks.png`

## Quick Start (Local Development)

> Tests can be run on any machine with Python 3.9+. The full application stack requires Docker.

Clone the repo:

```bash
git clone https://github.com/zuhaib31/taskflow.git
cd taskflow
```

Create a Python virtual environment and run the tests:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-test.txt
pytest
```

You should see `40 passed`.

To run the full application stack with Docker:

```bash
cp .env.example .env
# Edit .env with your own secrets (see comments in the file)
docker compose up -d
```

The application is available at `http://localhost:5000`.

## Full Deployment to AWS

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the complete step-by-step deployment procedure, including EC2 provisioning, Jenkins setup, and pipeline configuration.

## Project Documentation

| Document | Contents |
|----------|----------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture, component descriptions, design decisions, and known limitations |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Step-by-step deployment guide from a fresh EC2 instance |
| [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Database tables, relationships, and indexing strategy |
| [docs/LEARNINGS.md](docs/LEARNINGS.md) | What I learned building this, problems I solved, and an honest scope statement |

## Repository Structure
taskflow/
├── app/                    # Flask application
│   ├── init.py        # Application factory
│   ├── config.py          # Environment-based configuration
│   ├── models/            # User, Project, Task models
│   ├── routes/            # Blueprints: main, auth, projects, tasks
│   ├── templates/         # Jinja2 templates
│   ├── static/css/        # Stylesheet
│   └── utils/             # Validators and decorators
├── tests/                  # pytest suite (40 tests)
│   ├── conftest.py        # Pytest fixtures and mock setup
│   ├── test_validators.py # Unit tests for input validation
│   └── test_routes.py     # Integration tests for routes
├── migrations/             # SQL schema migrations
├── jenkins/                # Custom Jenkins image
│   └── Dockerfile
├── docs/                   # Architecture, deployment, learnings docs
├── scripts/                # Helper scripts
├── Dockerfile              # Application container definition
├── docker-compose.yml      # Multi-container orchestration
├── Jenkinsfile             # CI/CD pipeline as code
├── requirements.txt        # Production dependencies
├── requirements-test.txt   # Test-only dependencies (no MySQL driver)
├── pytest.ini              # Pytest configuration
└── .env.example            # Environment variable template
## Tests

40 automated tests covering input validation and HTTP route behavior:
tests/test_validators.py - 27 tests for username, email, password, project, task validators
tests/test_routes.py     - 13 tests for health endpoint, auth gating, route rendering, 404 handling
Tests run on every pipeline build inside an ephemeral Python container. A failing test blocks the build, the deploy, and the health check stages - the broken code never reaches the live app.

## Author

**Zohaib Ali** - Transitioning from operations analytics into cloud and DevOps engineering. This project is part of my portfolio toward an entry-level cloud or DevOps role.

- GitHub: [@zuhaib31](https://github.com/zuhaib31)

## License

MIT - see [LICENSE](LICENSE).
