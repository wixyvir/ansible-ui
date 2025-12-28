# Ansible UI Backend

Django REST Framework backend for the Ansible UI project. This backend processes Ansible execution logs, stores them in a database, and provides a REST API for the frontend to consume.

## Overview

The backend is part of the Ansible UI project (v0.2.0) and serves as the data layer for displaying Ansible play execution results. It uses Django 5.2+ with Django REST Framework for API endpoints.

## Technology Stack

- **Python**: 3.12+
- **Django**: 5.2+
- **Django REST Framework**: 3.14+
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

### Hello Endpoint

**URL**: `/api/hello`
**Method**: `GET`
**Description**: Simple endpoint to verify the backend is running

**Example Request**:
```bash
curl http://localhost:8000/api/hello
```

**Example Response**:
```json
{
  "message": "Hello from Ansible UI Backend",
  "version": "0.2.0",
  "status": "running"
}
```

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

### Planned Features (v0.2.0+)

- **Database Models**: Host, Play, TaskSummary models matching frontend types
- **Ansible Log Parsing**: Process and store Ansible execution results
- **CRUD Endpoints**: Full REST API for plays, hosts, and tasks
- **Authentication**: User authentication and authorization
- **WebSocket Support**: Real-time updates for live play monitoring
- **File Upload**: Upload and parse Ansible log files
- **Filtering & Search**: Query plays by status, date, hostname, etc.

### Upcoming API Endpoints (Future)

- `GET /api/hosts/` - List all hosts
- `GET /api/hosts/{id}/` - Get host details with plays
- `GET /api/plays/` - List all plays
- `GET /api/plays/{id}/` - Get play details
- `POST /api/logs/upload/` - Upload Ansible log file for processing

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
