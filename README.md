# TaskFlow

A task and project management web application built with Flask and MySQL, deployed using Docker and a Jenkins-powered CI/CD pipeline on AWS EC2.

## Status

**Work in progress** - Currently in development

## Tech Stack

- **Backend:** Python Flask
- **Database:** MySQL 8.0
- **Containerization:**Docker, Docker Compose
- **CI/CD:** Jenkins
- **Cloud:** AWS EC2
- **Version Control:** Git, GitHub

## Project Goals

Build a production-grade task management system while demonstrating:
- Full-stack web development
- Database design and integration
- Containerization with Docker
- Automated CI/CD pipelines
- Cloud deployment on AWS
- DevOps best practices

## Features (Planned)

- [x] Project structure and configuration management
- [x] Database schema design
- [x] Flask application factory pattern
- [x] Health check endpoint
- [x] User registration and authentication
- [x] Password hashing with Werkzeug
- [x] Session-based authentication
- [x] Protected routes with @login_required
- [x] Create and manage projects (CRUD)
- [x] Ownership enforcement (IDOR protection)
- [x] Custom 404 error page
- [x] Create, update, and delete tasks
- [x] Task assignment to projects
- [x] Status tracking (To Do, In Progress, Done)
- [x] Priority levels (Low, Medium, High)
- [x] Due dates on tasks
- [x] Kanban-style task board
- [x] Quick status change buttons
- [x] Dashboard with project and task statistics
- [x] Docker containerization
- [x] Multi-container orchestration with Docker Compose
- [ ] CI/CD pipeline with Jenkins
- [ ] AWS EC2 deployment

## Documentation
More documentation coming as the project develops:
- Architecture overview
- Deployment guide
- Local development setup

## Running with Docker

This is the supported way to run TaskFlow. Both the Flask app and MySQL run in containers; you don't need Python or MySQL installed locally.

### Prerequisites

- Docker and Docker Compose

### Configuration

Copy the example environment file and fill in real values:

```bash
cp .env.example .env
```

Generate a strong SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Paste the output into `.env` as the value of `SECRET_KEY`. Set strong values for `MYSQL_ROOT_PASSWORD` and `MYSQL_PASSWORD` as well.

### Start the stack

```bash
docker compose up -d
```

This builds the Flask image, pulls MySQL 8.0, runs the database schema migration automatically, and starts both containers on a private network.

The application becomes available at:

- `http://localhost:5000` (when running locally)
- `http://<server-ip>:5000` (when running on a remote server)

### View logs

```bash
docker compose logs -f web    # Flask app logs
docker compose logs -f mysql  # Database logs
```

### Stop the stack

```bash
docker compose down           # Stop containers, keep data
docker compose down -v        # Stop and delete all data (fresh start)
```

### Project Structure

```
taskflow/
├── app/                    # Flask application package
│   ├── __init__.py        # Application factory
│   ├── config.py          # Environment-based configuration
│   ├── models/            # Data models (User, Project, Task)
│   ├── routes/            # Blueprint modules (auth, projects, tasks)
│   ├── templates/         # Jinja2 templates
│   └── static/            # CSS, JS, images
├── migrations/            # SQL migration files
├── scripts/               # Helper scripts
├── tests/                 # pytest test files
├── docs/                  # Documentation
├── Dockerfile             # Container definition for the Flask app
├── docker-compose.yml     # Multi-container orchestration
├── run.py                 # Application entry point
└── requirements.txt       # Python dependencies
```

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Docker and Docker Compose (recommended)

### Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### Database Setup

Migrations live in `migrations/`. They can be run via:

```bash
python scripts/init_db.py
```

### Project Structure

```
taskflow/
├── app/                   # Flask application package
│   ├── __init__.py        # Application factory
│   ├── config.py          # Environment-based configuration
│   ├── routes/            # Blueprint modules
│   ├── templates/         # Jinja2 templates
│   └── static/            # CSS, JS, images
├── migrations/            # SQL migration files
├── scripts/               # Helper scripts
├── tests/                 # pytest test files
├── docs/                  # Documentation
├── run.py                 # Application entry point
└── requirements.txt       # Python dependencies
```

## Author
Built by Zohaib as a portfolio project demonstrating DevOps and full-stack capabilities.

## License


