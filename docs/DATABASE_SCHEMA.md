# Database Schema

## Overview

TaskFlow uses a MySQL relational database with 4 main tables organized around users, projects, tasks, and comments.

## Entity Relationship Diagram
┌─────────────┐
│   users     │
└──────┬──────┘
│ 1
│
│ N
┌──────▼──────┐
│  projects   │
└──────┬──────┘
│ 1
│
│ N
┌──────▼──────┐         ┌─────────────┐
│   tasks     │◄────────┤  comments   │
└─────────────┘ 1     N └─────────────┘

## Tables

### `users`

Stores user accounts and authentication data.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Display name |
| `email` | VARCHAR(120) | UNIQUE, NOT NULL | Login identifier |
| `password_hash` | VARCHAR(255) | NOT NULL | Werkzeug-hashed password |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | |

**Indexes:**
- `idx_users_email` on `email` (lookup during login)

### `projects`

Each user can have multiple projects.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | |
| `user_id` | INT | NOT NULL, FOREIGN KEY → users(id) | Owner |
| `name` | VARCHAR(100) | NOT NULL | Project name |
| `description` | TEXT | | Optional details |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | |

**Indexes:**
- `idx_projects_user_id` on `user_id` (find user's projects)

**On Delete:** CASCADE (deleting a user deletes their projects)

### `tasks`

Tasks belong to a project.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | |
| `project_id` | INT | NOT NULL, FOREIGN KEY → projects(id) | |
| `title` | VARCHAR(200) | NOT NULL | |
| `description` | TEXT | | |
| `status` | ENUM | NOT NULL, DEFAULT 'todo' | 'todo', 'in_progress', 'done' |
| `priority` | ENUM | NOT NULL, DEFAULT 'medium' | 'low', 'medium', 'high' |
| `due_date` | DATE | | Optional deadline |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | |

**Indexes:**
- `idx_tasks_project_id` on `project_id`
- `idx_tasks_status` on `status` (filter by status)

**On Delete:** CASCADE

### `comments`

Comments on tasks.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | INT | PRIMARY KEY, AUTO_INCREMENT | |
| `task_id` | INT | NOT NULL, FOREIGN KEY → tasks(id) | |
| `user_id` | INT | NOT NULL, FOREIGN KEY → users(id) | Author |
| `content` | TEXT | NOT NULL | |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | |

**Indexes:**
- `idx_comments_task_id` on `task_id`

**On Delete:** CASCADE (when task or user deleted)

## Design Decisions

### Why ENUMs for status and priority?
ENUMs enforce valid values at the database level. Trying to insert `status = 'banana'` will fail. This prevents bad data even if application validation is bypassed.

### Why TIMESTAMP for both created_at and updated_at?
- `created_at` is set once on insert
- `updated_at` automatically updates on every modification — useful for "last modified" displays and audit trails

### Why CASCADE delete?
If a user deletes their account, all their projects, tasks, and comments should go too. CASCADE handles this at the database level rather than requiring application code to clean up.

### Why VARCHAR(255) for password_hash?
Werkzeug's `generate_password_hash` produces hashes ~100 characters long. 255 gives plenty of room and is a common safe choice.