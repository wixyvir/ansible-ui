# Ansible UI Backend

Django REST Framework backend for the Ansible UI project. This backend processes Ansible execution logs, stores them in a database, and provides a REST API for the frontend to consume.

## Overview

The backend is part of the Ansible UI project (v0.3.0) and serves as the data layer for displaying Ansible play execution results. It uses Django 5.2+ with Django REST Framework for API endpoints.

## Technology Stack

- **Python**: 3.12+
- **Django**: 5.2+
- **Django REST Framework**: 3.14+
- **ansible-output-parser**: Library for parsing Ansible playbook output
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **CORS**: django-cors-headers for frontend communication
- **Dependency Management**: Poetry

## Project Structure

```
backend/
├── ansible_ui/          # Main Django project
│   ├── settings.py     # Configuration
│   ├── urls.py         # Root URL routing
│   ├── wsgi.py         # WSGI application
│   └── asgi.py         # ASGI application
├── api/                # API Django app
│   ├── views.py        # API views
│   ├── urls.py         # API URL routes
│   ├── models.py       # Database models
│   ├── serializers.py  # DRF serializers
│   ├── admin.py        # Django admin configuration
│   ├── services/       # Business logic services
│   │   └── log_parser.py  # Ansible log parsing service
│   ├── templates/      # Django admin templates
│   │   └── admin/api/log/  # Custom admin templates
│   └── tests.py        # Test cases
├── manage.py           # Django management script
├── pyproject.toml      # Poetry dependencies
└── README.md           # This file
```

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Poetry (Python dependency manager)

### Installing Poetry

If you don't have Poetry installed:

```bash
# On Linux/macOS
curl -sSL https://install.python-poetry.org | python3 -

# On Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

For more installation options, visit: https://python-poetry.org/docs/#installation

### Setup

1. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```
   This creates a virtual environment and installs all required packages.

3. **Activate the virtual environment** (optional)
   ```bash
   poetry shell
   ```
   Note: You can run commands with `poetry run` prefix instead of activating the shell.

4. **Run database migrations**
   ```bash
   poetry run python manage.py migrate
   ```
   This sets up the SQLite database with Django's default tables.

5. **Start the development server**
   ```bash
   poetry run python manage.py runserver
   ```
   The server starts at `http://localhost:8000`

## API Endpoints

The backend uses Django REST Framework with a router-based URL configuration. All endpoints are prefixed with `/api/`.

### Logs

#### Upload and Parse Log

**URL**: `/api/logs/`
**Method**: `POST`
**Description**: Upload and parse an Ansible log file

**Request Body**:
```json
{
  "title": "Production Deploy 2024-01-15",
  "raw_content": "PLAY [Setup Web Server] ***...\nPLAY RECAP ***..."
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/logs/ \
  -H "Content-Type: application/json" \
  -d '{"title": "My Log", "raw_content": "PLAY [Test] ***\n\nTASK [Gathering Facts] ***\nok: [server1]\n\nPLAY RECAP ***\nserver1 : ok=1 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0"}'
```

**Success Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Log",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "hosts": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "hostname": "server1",
      "plays": [
        {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "name": "Test",
          "date": null,
          "status": "ok",
          "tasks": {"ok": 1, "changed": 0, "failed": 0},
          "line_number": 1,
          "order": 0
        }
      ]
    }
  ],
  "host_count": 1
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "error": "No hosts found in log",
  "detail": "The parser could not find any PLAY RECAP section",
  "parser_type": "play",
  "raw_content_preview": "..."
}
```

#### Get Log Details

**URL**: `/api/logs/{id}/`
**Method**: `GET`
**Description**: Retrieve a specific log with all hosts and plays

**Example Request**:
```bash
curl http://localhost:8000/api/logs/550e8400-e29b-41d4-a716-446655440000/
```

**Example Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Deployment Log",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "hosts": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "hostname": "web-01.example.com",
      "plays": [
        {
          "id": "770e8400-e29b-41d4-a716-446655440002",
          "name": "Setup Web Server",
          "date": "2024-01-15T10:30:00Z",
          "status": "ok",
          "tasks": {
            "ok": 10,
            "changed": 3,
            "failed": 0
          }
        }
      ]
    }
  ],
  "host_count": 1
}
```

#### Get Log Hosts

**URL**: `/api/logs/{id}/hosts/`
**Method**: `GET`
**Description**: List all hosts for a specific log with their plays

**Example Request**:
```bash
curl http://localhost:8000/api/logs/550e8400-e29b-41d4-a716-446655440000/hosts/
```

**Example Response**:
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "hostname": "web-01.example.com",
    "plays": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "name": "Setup Web Server",
        "date": "2024-01-15T10:30:00Z",
        "status": "changed",
        "tasks": {
          "ok": 8,
          "changed": 5,
          "failed": 0
        }
      }
    ]
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "hostname": "web-02.example.com",
    "plays": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440003",
        "name": "Setup Web Server",
        "date": "2024-01-15T10:31:00Z",
        "status": "ok",
        "tasks": {
          "ok": 13,
          "changed": 0,
          "failed": 0
        }
      }
    ]
  }
]
```

### Response Data Types

#### Log
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| title | string | Log title |
| uploaded_at | ISO datetime | Upload timestamp |
| hosts | array | List of hosts (nested) |
| host_count | integer | Number of hosts |

#### Host
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| hostname | string | Server hostname/FQDN |
| plays | array | List of plays (nested) |

#### Play
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| name | string | Play name |
| date | ISO datetime or null | Execution timestamp (null for raw stdout logs) |
| status | string | ok, changed, or failed |
| tasks | object | Task summary counts |
| line_number | integer or null | Line number in raw log where play starts |
| order | integer | Play order position (0-indexed) |

#### TaskSummary
| Field | Type | Description |
|-------|------|-------------|
| ok | integer | Successfully completed tasks |
| changed | integer | Tasks that made changes |
| failed | integer | Failed tasks |

## Development Workflow

### Running the Development Server

```bash
poetry run python manage.py runserver
```

The server runs on `http://localhost:8000` by default. The frontend (Vite dev server on `http://localhost:5173`) is configured to communicate with this backend via CORS.

### Running Migrations

After creating or modifying models:

```bash
# Create migration files
poetry run python manage.py makemigrations

# Apply migrations
poetry run python manage.py migrate
```

### Creating a Superuser (for Django Admin)

```bash
poetry run python manage.py createsuperuser
```

Access the admin panel at `http://localhost:8000/admin/`

### Django Admin Features

The admin interface includes enhanced features for managing Ansible logs:

- **Log Admin**: View logs with host count, play count, and failure status badges
- **Host Admin**: View hosts with play status summary and latest play date
- **Play Admin**: View plays with colored status badges and task summaries
- **Test Submission**: Custom page at `/admin/api/log/submit-test/` for testing log parsing
- **Custom Filters**: Filter by failures, play status, task counts

### Running Tests (Future)

```bash
poetry run pytest
```

### Code Quality

The project uses three linting tools:
- **autoflake**: Removes unused imports and variables
- **flake8**: Python style guide enforcement
- **black**: Code formatting

#### Check for Issues (no modifications)

```bash
# Run all lint checks
poetry run poe lint

# Run individual checks
poetry run poe lint-check    # autoflake only
poetry run poe flake8-check  # flake8 only
poetry run poe black-check   # black only
```

#### Fix Issues (modifies files)

```bash
# Fix all lint issues
poetry run poe fix

# Run individual fixes
poetry run poe lint-fix   # autoflake fix
poetry run poe black-fix  # black fix
```

## Configuration

### CORS Settings

The backend is configured to allow requests from the frontend development server:

- **Allowed Origins**: `http://localhost:5173` (Vite dev server)

To add more origins, update `CORS_ALLOWED_ORIGINS` in [ansible_ui/settings.py](ansible_ui/settings.py).

### Database

Currently using SQLite for development (`db.sqlite3`). For production, consider PostgreSQL or MySQL.

### REST Framework

- **Permissions**: `AllowAny` (open for development)
- **Pagination**: Page number pagination with 100 items per page

Update `REST_FRAMEWORK` settings in [ansible_ui/settings.py](ansible_ui/settings.py) as needed.

## Relationship to Frontend

The backend serves the React frontend located in the `../frontend/` directory. The frontend currently uses mock data, which will be replaced by API calls to this backend as development progresses.

**Frontend Dev Server**: `http://localhost:5173`
**Backend Dev Server**: `http://localhost:8000`

## Future Development

### Planned Features

- **Remaining API Endpoints**:
  - `GET /api/logs/` - List all logs with pagination
  - `GET /api/hosts/` - List all hosts
  - `GET /api/hosts/{id}/` - Get host details with plays
  - `GET /api/plays/` - List all plays
  - `GET /api/plays/{id}/` - Get play details
- **Authentication**: User authentication and authorization
- **WebSocket Support**: Real-time updates for live play monitoring
- **Filtering & Search**: Query plays by status, date, hostname, etc.

## Troubleshooting

### Port Already in Use

If port 8000 is occupied, specify a different port:

```bash
poetry run python manage.py runserver 8080
```

Update `CORS_ALLOWED_ORIGINS` in settings if you change the port.

### Poetry Virtual Environment Issues

If dependencies don't install correctly:

```bash
# Remove existing virtual environment
poetry env remove python3.12

# Reinstall
poetry install
```

### CORS Errors

If the frontend can't connect to the backend:

1. Verify the backend is running on `http://localhost:8000`
2. Check `CORS_ALLOWED_ORIGINS` includes the frontend URL
3. Ensure `corsheaders` middleware is in `MIDDLEWARE` in settings

## Contributing

When adding new features:

1. Create database models in [api/models.py](api/models.py)
2. Create serializers in [api/serializers.py](api/serializers.py)
3. Implement views in [api/views.py](api/views.py)
4. Add URL patterns to [api/urls.py](api/urls.py)
5. Write tests in [api/tests.py](api/tests.py)
6. Run `poetry run poe lint` to check code quality
7. Update this README with new endpoints

## CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/python-lint.yml`) that automatically runs lint checks on:
- Push to `main` branch
- Pull requests targeting `main` branch

The workflow only triggers when backend files are modified.

## License

This project is for internal use. Part of the Ansible UI project.
