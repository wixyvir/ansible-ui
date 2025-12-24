# Ansible UI

A modern web application for visualizing Ansible playbook execution results with a clean, professional interface.

## Overview

Ansible UI provides DevOps teams and system administrators with an intuitive way to monitor and understand Ansible playbook execution results. Instead of parsing through terminal logs, users can see hosts, plays, and task summaries in a beautifully designed dark-mode interface.

## Features

- **Visual Host Overview**: Display all hosts with their associated plays
- **Play Status Tracking**: Color-coded status indicators (OK, Changed, Failed)
- **Task Summaries**: Detailed task counts for each play execution
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Dark Mode UI**: Terminal-friendly aesthetic with excellent contrast
- **Log Management**: Upload and organize multiple Ansible execution logs

## Technology Stack

### Frontend
- React 18.3 with TypeScript
- Vite for fast development and builds
- Tailwind CSS for styling
- Lucide React for icons

### Backend
- Django 5.2 with Django REST Framework
- Python 3.12+
- SQLite (development) / PostgreSQL (production)
- Poetry for dependency management

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- Poetry (install via `curl -sSL https://install.python-poetry.org | python3 -`)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Backend Setup

```bash
cd backend
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Backend runs at: `http://localhost:8000`

## Project Structure

```
ansible-ui/
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── types/         # TypeScript definitions
│   │   └── App.tsx        # Main app component
│   └── package.json
│
├── backend/           # Django REST API backend
│   ├── ansible_ui/    # Django project config
│   ├── api/          # REST API app
│   │   ├── models.py      # Database models
│   │   ├── serializers.py # DRF serializers
│   │   └── views.py       # API views
│   └── pyproject.toml
│
├── CLAUDE.md         # Detailed project documentation
└── README.md         # This file
```

## Data Model

The application uses a hierarchical structure:

```
Log (uploaded Ansible log file)
 └── Host (servers in the log)
      └── Play (play executions)
           └── TaskSummary (ok/changed/failed counts)
```

### Key Models

**Log**: Represents an uploaded Ansible log file
- Title, upload timestamp, raw content
- One-to-many relationship with hosts

**Host**: Represents a server in a log
- Hostname, unique per log
- One-to-many relationship with plays

**Play**: Represents an Ansible play execution
- Name, date, status (ok/changed/failed)
- Task counts (ok, changed, failed)

## Current Status

**Version 0.2.0** - Backend Foundation Complete

✅ Implemented:
- Complete frontend UI with responsive design
- Django backend with REST Framework
- Database models (Log, Host, Play)
- DRF serializers with frontend compatibility
- Database migrations

🚧 In Progress:
- API endpoints (views/viewsets)
- Ansible log parsing
- Frontend-backend integration

📋 Planned:
- File upload functionality
- Historical log viewing
- Search and filtering
- Authentication
- Real-time updates

## Documentation

For detailed documentation including:
- Component architecture
- API design
- Development workflow
- Design decisions
- Troubleshooting guide

See [CLAUDE.md](CLAUDE.md)

## Development

### Running Both Servers

Terminal 1 (Frontend):
```bash
cd frontend && npm run dev
```

Terminal 2 (Backend):
```bash
cd backend && poetry run python manage.py runserver
```

### Available Scripts

**Frontend**:
- `npm run dev` - Start dev server
- `npm run build` - Production build
- `npm run lint` - Run ESLint

**Backend**:
- `poetry run python manage.py runserver` - Start dev server
- `poetry run python manage.py migrate` - Apply migrations
- `poetry run python manage.py makemigrations` - Create migrations
- `poetry run python manage.py createsuperuser` - Create admin user

## Database

The application uses SQLite for development. To reset the database:

```bash
cd backend
rm db.sqlite3
poetry run python manage.py migrate
```

## Contributing

1. Follow TypeScript types defined in `frontend/src/types/`
2. Use Tailwind utilities instead of custom CSS
3. Maintain dark mode aesthetic
4. Write backend models that mirror frontend types
5. Run `npm run lint` before committing frontend changes

## Future Roadmap

### v0.2.x - API Endpoints
- Implement DRF views/viewsets
- Parse Ansible JSON output
- Create REST endpoints for all models
- Frontend integration

### v0.3.0 - Enhanced Features
- Log upload functionality
- Historical log viewing with pagination
- Advanced filtering and search
- Export capabilities (JSON, CSV)

### v0.4.0+ - Advanced Features
- User authentication and authorization
- Real-time updates via WebSockets
- Email/Slack notifications
- Analytics dashboard
- Docker containerization
- PostgreSQL migration for production

## License

Internal use project.

## Support

For issues, questions, or contributions, please refer to the comprehensive documentation in [CLAUDE.md](CLAUDE.md).
