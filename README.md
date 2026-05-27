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
## Features (Planned)
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
- [ ] Create, update, and delete tasks
- [ ] Task assignment to projects
- [ ] Status tracking (To Do, In Progress, Done)
- [ ] Priority levels (Low, Medium, High)
- [ ] Comments on tasks
- [ ] Dashboard with project statistics
- [ ] Docker containerization
- [ ] CI/CD pipeline with Jenkins
- [ ] AWS EC2 deployment

## Documentation
More documentation coming as the project develops:
- Architecture overview
- Deployment guide
- Local development setup

## Local Development

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


