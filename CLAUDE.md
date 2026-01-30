# Ansible UI - Project Documentation

## Overview

Ansible UI is a modern web application designed to display comprehensive views of Ansible Play execution results in a clean, professional, and visually appealing interface. The application focuses on presenting hosts and their associated plays with detailed task summaries.

## Project Purpose

The primary goal is to provide DevOps teams and system administrators with an intuitive way to monitor and understand Ansible playbook execution results at a glance. Instead of parsing through terminal logs, users can see:

- Which hosts were targeted by Ansible executions
- Multiple plays executed on each host
- The overall status of each play (OK, Changed, Failed)
- Detailed task counts for each play
- Execution timestamps for each play

## Technology Stack

### Frontend
- **React 18.3.1**: Modern UI library with hooks and functional components
- **TypeScript 5.6**: Type-safe development with enhanced IDE support
- **Vite 6**: Lightning-fast build tool and dev server
- **Tailwind CSS 3.4**: Utility-first CSS framework
- **Lucide React 0.460**: Clean, consistent icon library
- **react-syntax-highlighter**: Code syntax highlighting for error messages
- **ESLint**: Code linting and quality enforcement

### Backend
- **Python 3.12+**: Modern Python with performance improvements
- **Django 5.2**: High-level web framework
- **Django REST Framework 3.16**: Powerful toolkit for building Web APIs
- **Poetry**: Dependency management and packaging
- **python-decouple**: Environment variable configuration management
- **SQLite**: Development database (PostgreSQL for production)
- **django-cors-headers**: CORS support for frontend communication
- **ansible-output-parser**: Library for parsing Ansible playbook output
- **Poe the Poet**: Task runner for linting and code quality commands

### Production Deployment
- **Docker**: Multi-stage containerization with Docker Compose
- **gunicorn**: WSGI HTTP server for Django
- **nginx**: Reverse proxy and static file server
- **PostgreSQL 13**: Production database
- **Rocky Linux 9**: Base container image

## Architecture

### Project Structure

```
ansible-ui/
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── types/         # TypeScript type definitions
│   │   ├── App.tsx        # Main application component
│   │   └── main.tsx       # React entry point
│   └── package.json       # Frontend dependencies
│
├── backend/               # Django REST API backend
│   ├── ansible_ui/       # Django project configuration
│   │   ├── settings.py   # Django settings (CORS, DRF, decouple)
│   │   └── urls.py       # Root URL routing
│   ├── api/              # REST API Django app
│   │   ├── views.py      # API view implementations
│   │   ├── urls.py       # API URL routing
│   │   ├── models.py     # Database models
│   │   ├── serializers.py # DRF serializers
│   │   ├── admin.py      # Django admin configuration
│   │   ├── services/     # Business logic services
│   │   │   └── log_parser.py  # Ansible log parsing service
│   │   └── templates/    # Django admin templates
│   │       └── admin/api/log/  # Custom admin templates
│   ├── manage.py         # Django management script
│   ├── pyproject.toml    # Poetry dependencies
│   ├── .env.example      # Environment variables template
│   └── README.md         # Backend documentation
│
├── docker/                # Docker configuration files
│   ├── entrypoint.api.sh # API container startup script
│   └── nginx.conf        # nginx reverse proxy configuration
│
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Docker Compose orchestration
├── .dockerignore         # Docker build context exclusions
├── .env.production       # Production environment template
├── CLAUDE.md             # This file
└── .gitignore            # Git ignore patterns
```

### Frontend Component Structure

```
frontend/src/
├── components/
│   ├── CollapsibleTaskSection.tsx  # Expandable task list with lazy loading
│   ├── PlayCard.tsx        # Displays individual play with task summaries
│   ├── PlayHeader.tsx      # (Legacy) Displays play title and execution date
│   ├── ServerCard.tsx      # Host card displaying multiple plays
│   └── StatusBadge.tsx     # Reusable status indicator badge with expand support
├── services/
│   └── api.ts              # Backend API client functions
├── types/
│   └── ansible.ts          # TypeScript type definitions
├── pages/
│   └── LogPage.tsx         # Log detail page with hosts and plays
├── App.tsx                 # Main application component with routing
├── main.tsx                # React app entry point
└── index.css               # Global styles and Tailwind directives
```

### Data Model

The application uses a hierarchical data structure to organize Ansible execution data:

```
Log (uploaded Ansible log file)
 └── Host (servers in the log)
      └── Play (play executions on the host)
           ├── TaskSummary (aggregated task counts: ok/changed/failed)
           └── Task (individual task executions with status and failure details)
```

#### Log
Represents an uploaded Ansible log file:
```typescript
interface Log {
  id: string;           // Unique identifier
  title: string;        // User-provided log title
  uploaded_at: string;  // Upload timestamp
  hosts: Host[];        // Array of hosts in this log
}
```

**Backend Model** (Django):
- `title`: CharField - Log title
- `uploaded_at`: DateTimeField - Auto-set on creation
- `raw_content`: TextField - Full raw log content for re-parsing
- Cascading delete: Deleting a log removes all associated hosts and plays

#### Host
Represents a single server with its associated plays:
```typescript
interface Host {
  id: string;           // Unique identifier
  hostname: string;     // Server hostname/FQDN
  plays: Play[];        // Array of plays executed on this host
}
```

**Backend Model** (Django):
- `log`: ForeignKey to Log - Every host belongs to a log
- `hostname`: CharField - Indexed for performance
- `unique_together`: Hostname must be unique within each log
- Same hostname can appear in different logs

#### Play
Represents a single Ansible play execution:
```typescript
interface Play {
  id: string;           // Unique identifier
  name: string;         // Play name (e.g., "Setup Web Server")
  date: string;         // Execution timestamp (nullable)
  status: PlayStatus;   // Play status (ok/changed/failed)
  tasks: TaskSummary;   // Task execution counts for this play
  line_number: number;  // Line number in raw log where play starts
  order: number;        // Play order position (0-indexed)
}
```

**Backend Model** (Django):
- `host`: ForeignKey to Host
- `name`: CharField - Play name
- `date`: DateTimeField - Execution timestamp (nullable for raw stdout logs)
- `status`: CharField with choices (ok/changed/failed)
- `tasks_ok`, `tasks_changed`, `tasks_failed`: IntegerFields
- `line_number`: PositiveIntegerField - Line number in raw log (nullable)
- `order`: PositiveIntegerField - Play order position for sorting
- `tasks` property returns TaskSummary dict for API serialization
- Database indexes on `(host, order)` and `(status, -date)` for query performance

#### TaskSummary
Aggregated task results for a play:
```typescript
interface TaskSummary {
  ok: number;           // Successfully completed tasks
  changed: number;      // Tasks that made changes
  failed: number;       // Failed tasks
}
```

#### PlayStatus
```typescript
type PlayStatus = 'ok' | 'changed' | 'failed';
```

#### Task
Represents an individual Ansible task execution on a specific host:
```typescript
interface Task {
  id: string;           // Unique identifier
  name: string;         // Task name (e.g., "Install nginx")
  order: number;        // Task order position (0-indexed)
  line_number: number;  // Line number in raw log where task starts (nullable)
  status: TaskStatus;   // Task status for this host
  failure_message: string | null;  // Error message when task fails
}
```

**Backend Model** (Django):
- `play`: ForeignKey to Play - Every task belongs to a play (which belongs to a host)
- `name`: CharField - Task name (max 500 chars)
- `order`: PositiveIntegerField - Task execution order (0-indexed)
- `line_number`: PositiveIntegerField - Line in raw log where task starts (nullable)
- `status`: CharField with choices (ok/changed/failed/fatal/skipping/unreachable/ignored/rescued)
- `failure_message`: TextField - Error message when task fails (nullable)
- Database indexes on `(play, order)` and `(status)` for query performance

#### TaskStatus
```typescript
type TaskStatus = 'ok' | 'changed' | 'failed' | 'fatal' | 'skipping' | 'unreachable' | 'ignored' | 'rescued';
```

**Note:** Both "failed" and "fatal" represent task failures. When filtering by status, requesting "failed" returns both "failed" and "fatal" tasks.

### Component Design

#### ServerCard
- Card-based design with dark slate background
- Server icon with color-coded status based on plays (red if any play failed, blue if any changed, green if all OK)
- Hostname prominently displayed
- Contains multiple PlayCard components
- Rounded corners with subtle shadow for depth

#### PlayCard
- Nested card design with lighter slate background
- Displays play name prominently with color-coded status
- Shows execution timestamp with calendar icon
- Three CollapsibleTaskSection components for OK/Changed/Failed task counts
- Expandable to reveal task details per status
- Compact design suitable for multiple plays per host

#### CollapsibleTaskSection
- Wraps StatusBadge with expand/collapse functionality
- Lazy-loads tasks from API on first expand
- Caches fetched tasks (no refetch on collapse/expand)
- Shows loading spinner while fetching
- Displays task names with failure messages for failed tasks
- Failure messages in code blocks with JSON syntax highlighting (react-syntax-highlighter with oneDark theme)
- Copy to clipboard button appears on hover for failure messages
- Sections with count 0 are disabled (grayed out, non-clickable)
- Multiple sections can be expanded simultaneously (independent mode)

#### StatusBadge
- Reusable component for displaying status counts
- Color-coded backgrounds with semi-transparent overlays
- Border styling for definition
- Flex layout with label and count
- Optional props: `disabled`, `expanded`, `showChevron`, `onClick`
- Supports interactive expand/collapse with chevron indicator
- Disabled state shows grayed out, non-clickable badge

#### PlayHeader (Legacy)
- Legacy component no longer used in main app
- Previously displayed play title and execution date
- Kept for potential future use

### Styling System

#### Color Palette (Dark Mode)
- **Background**: `bg-slate-900` - Deep dark slate
- **Host Cards**: `bg-slate-800` with `border-slate-700` - Medium dark slate
- **Play Cards**: `bg-slate-700` with `border-slate-600` - Lighter slate (nested)
- **Text Primary**: `text-slate-100` - Light gray
- **Text Secondary**: `text-slate-300` - Medium gray
- **Text Muted**: `text-slate-400` - Darker gray

#### Status Colors
- **OK**: Green theme (`bg-green-900/50`, `text-green-400`, `border-green-700`)
- **Changed**: Blue theme (`bg-blue-900/50`, `text-blue-400`, `border-blue-700`)
- **Failed**: Red theme (`bg-red-900/50`, `text-red-400`, `border-red-700`)

#### Responsive Layout
- **Mobile**: Single column grid
- **Tablet (md)**: 2-column grid
- **Desktop (lg)**: 3-column grid
- Consistent gap spacing and padding

## Development

### Getting Started

#### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```
   Server starts at `http://localhost:5173`

#### Backend Setup

1. **Navigate to Backend Directory**
   ```bash
   cd backend
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install Dependencies**
   ```bash
   poetry install
   ```

4. **Run Database Migrations**
   ```bash
   poetry run python manage.py migrate
   ```

5. **Start Development Server**
   ```bash
   poetry run python manage.py runserver
   ```
   Server starts at `http://localhost:8000`

### Environment Configuration

The backend uses `python-decouple` for environment variable management. Settings can be configured via environment variables or a `.env` file.

**Available Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET` | Django secret key | Insecure dev key |
| `DJANGO_PROD` | Production mode (enables PostgreSQL, disables DEBUG) | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | Empty |
| `DJANGO_TZ` | Timezone | `UTC` |
| `DJANGO_STATIC_ROOT` | Static files directory | `None` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:5173` |
| `DB_NAME` | PostgreSQL database name | Required if `DJANGO_PROD=True` |
| `DB_USERNAME` | PostgreSQL username | Required if `DJANGO_PROD=True` |
| `DB_PASSWORD` | PostgreSQL password | Required if `DJANGO_PROD=True` |
| `DB_HOSTNAME` | PostgreSQL host | Required if `DJANGO_PROD=True` |
| `DB_PORT` | PostgreSQL port | Required if `DJANGO_PROD=True` |

**Development** (no `.env` file needed - defaults work):
```bash
poetry run python manage.py runserver
```

**Production** (create `.env` file in backend directory):
```bash
DJANGO_PROD=True
DJANGO_SECRET=your-secure-secret-key
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_STATIC_ROOT=/var/www/static
DB_NAME=ansible_ui
DB_USERNAME=postgres
DB_PASSWORD=your-secure-password
DB_HOSTNAME=localhost
DB_PORT=5432
```

See [backend/.env.example](backend/.env.example) for a complete template.

### Docker Deployment

The project includes production-ready Docker configuration with multi-stage builds.

**Architecture:**
- **frontend-builder**: Builds React app with Node.js 20
- **backend-builder**: Builds Python package with Poetry
- **api**: Django application with gunicorn (Rocky Linux 9)
- **web**: nginx reverse proxy serving frontend and proxying API (Alpine Linux)
- **db**: PostgreSQL 13 database

**Quick Start:**

1. **Build images:**
   ```bash
   docker-compose build
   ```

2. **Configure environment:**
   ```bash
   cp .env.production .env
   # Edit .env with your secure values
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations and create superuser:**
   ```bash
   docker-compose exec api django-admin migrate
   docker-compose exec api django-admin createsuperuser
   ```

5. **Access the application:**
   - Frontend: http://localhost/
   - Admin: http://localhost/admin/
   - API: http://localhost/api/

**docker-compose.yml services:**
- `api`: Django backend (internal port 8000)
- `db`: PostgreSQL with persistent volume
- `web`: nginx (external port 80)

**nginx routing:**
- `/` → React frontend (SPA with fallback routing)
- `/api/` → Django API backend
- `/admin/` → Django admin interface
- `/static/` → Django static files

**Environment variables** (same as development, defined in `.env`):
- `DJANGO_PROD=True` (enables PostgreSQL, disables DEBUG)
- `DJANGO_SECRET` (secure random secret key)
- `DJANGO_ALLOWED_HOSTS` (comma-separated domains)
- `DB_*` variables for PostgreSQL connection

**Production notes:**
- Change all default passwords and secrets
- Use proper domain in `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
- Consider HTTPS termination (nginx + Let's Encrypt)
- Set up volume backups for PostgreSQL data
- Add health checks to docker-compose

### Development Workflow

**Running Both Servers**

For full-stack development, run both servers simultaneously:

Terminal 1 (Frontend):
```bash
cd frontend
npm run dev
```

Terminal 2 (Backend):
```bash
cd backend
poetry run python manage.py runserver
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Backend API: `http://localhost:8000/api/`

### Frontend Scripts

- `npm run dev` - Start Vite dev server with hot reload
- `npm run build` - TypeScript compilation + production build
- `npm run lint` - Run ESLint on codebase
- `npm run preview` - Preview production build locally

### Backend Scripts

- `poetry run python manage.py runserver` - Start Django dev server
- `poetry run python manage.py migrate` - Run database migrations
- `poetry run python manage.py makemigrations` - Create new migrations
- `poetry run python manage.py createsuperuser` - Create admin user
- `poetry run pytest` - Run tests (future)

**Poe Task Runner Commands** (recommended):
- `poetry run poe lint` - Run all lint checks (autoflake, flake8, black)
- `poetry run poe fix` - Auto-fix lint issues (autoflake + black)
- `poetry run poe lint-check` - Check for unused imports/variables
- `poetry run poe flake8-check` - Run flake8 style checks
- `poetry run poe black-check` - Check code formatting

### Frontend Data Flow

The frontend fetches data from the backend API:
- **Log Page** (`/log/:logId`): Fetches log with hosts and plays via `fetchLog(logId)`
- **Task Lists**: Lazy-loaded via `fetchTasks(playId, status)` when expanding status sections
- **Caching**: Tasks are cached in component state after first fetch
- **Error States**: Connection errors and 404s are handled with user-friendly messages

## Current Implementation

### v0.1.0 - Frontend Foundation
- Single-page display of Ansible execution results by host
- Host cards with status indicators based on play outcomes
- Multiple plays displayed per host with individual task summaries
- Color-coded badges for OK/Changed/Failed tasks per play
- Play names and execution timestamps
- Responsive grid layout
- Dark mode design with nested card hierarchy
- Static mock data (no backend integration yet)

### v0.2.0 - Backend Foundation
- **Django REST Framework Backend**: Python 3.12 with Django 5.2
- **Poetry Dependency Management**: Modern Python packaging and dependency resolution
- **API Structure**: RESTful API architecture with `/api/` prefix
- **Database Models**: Log, Host, and Play models implemented
- **DRF Serializers**: Complete serializers for all models with frontend compatibility
- **CORS Configuration**: Frontend-backend communication enabled
- **SQLite Database**: Initialized with Django migrations
- **Development Ready**: Comprehensive documentation and setup guides

### v0.3.0 - Log Parsing & Admin Interface
- **Ansible Log Parser Service**: Auto-detects and parses both raw stdout and timestamped log formats
- **POST `/api/logs/` Endpoint**: Upload and parse Ansible logs via API
- **Django Admin Interface**: Full admin panel with custom features
- **Admin Filters**: Custom filters for failures, play status, task counts
- **Admin Inlines**: View hosts and plays inline when editing logs
- **Test Submission Page**: Custom admin view for testing log parsing
- **Play Ordering**: Line number and order fields for accurate play sequencing
- **Poe Task Runner**: Integrated linting commands (autoflake, flake8, black)

### v0.3.1 - Task-Level Parsing
- **Task Model**: New model to store individual task executions per play per host
- **Task Extraction**: Parser extracts task names, status, and failure messages from logs
- **Per-Host Task Status**: Each task stores its status (ok/changed/failed/fatal/skipping/etc.) for the specific host
- **Failure Messages**: Task failures include error messages from Ansible output
- **Dedicated Task Endpoint**: `GET /api/plays/{id}/tasks/` returns task list with status filtering
- **Failed Filter Includes Fatal**: Filtering by "failed" returns both "failed" and "fatal" tasks
- **TaskAdmin**: Full admin interface for viewing and filtering tasks
- **TaskInline**: View tasks inline when editing plays in admin
- **Frontend Task Display**: Collapsible task sections in PlayCard with lazy-loaded task lists
- **CollapsibleTaskSection Component**: Expandable status badges that fetch and display tasks
- **fetchTasks API**: Frontend API function for fetching tasks by play ID and status

### v0.4.0 - Docker Containerization & Environment Configuration (Current)
- **python-decouple Integration**: Environment variable configuration for Django settings
- **Environment Variables**: `DJANGO_SECRET`, `DJANGO_PROD`, `DJANGO_ALLOWED_HOSTS`, `DB_*`, etc.
- **Multi-stage Dockerfile**: Separate build stages for frontend, backend, API, and web
- **Docker Compose**: Three-service architecture (api, db, web)
- **PostgreSQL Production Database**: Configured with persistent volumes
- **gunicorn**: Production WSGI server for Django
- **nginx Reverse Proxy**: Serves React frontend and proxies API/admin requests
- **Rocky Linux 9**: Base image for backend containers
- **Production Ready**: Full deployment configuration with security best practices
- **.env.production Template**: Example production environment configuration

### Database Models

**Log Model** - Represents uploaded Ansible log files
- Fields: `title`, `uploaded_at`, `raw_content`
- One-to-many relationship with Host
- Cascading deletes for data integrity

**Host Model** - Represents servers in logs
- Fields: `hostname`, `log` (ForeignKey), `created_at`, `updated_at`
- Unique hostname per log (same hostname can appear in different logs)
- One-to-many relationship with Play

**Play Model** - Represents Ansible play executions
- Fields: `name`, `date`, `status`, `tasks_ok`, `tasks_changed`, `tasks_failed`, `line_number`, `order`
- ForeignKey to Host
- Status choices: ok, changed, failed
- `line_number`: Line in raw log where play starts (for navigation)
- `order`: Play order position for correct sequencing
- `tasks` property returns TaskSummary dict
- `tasks_list` related name for accessing Task instances
- Database indexes for efficient querying

**Task Model** - Represents individual task executions
- Fields: `name`, `order`, `line_number`, `status`, `failure_message`
- ForeignKey to Play (cascading delete)
- Status choices: ok, changed, failed, fatal, skipping, unreachable, ignored, rescued
- `failure_message`: Stores error details when task fails
- One Task instance per task per play per host
- Database indexes on `(play, order)` and `(status)`

### Available Serializers

- **LogSerializer**: Full log with nested hosts
- **LogListSerializer**: Lightweight log listing
- **LogCreateSerializer**: For uploading new logs
- **HostSerializer**: Full host with nested plays
- **HostListSerializer**: Lightweight host listing
- **PlaySerializer**: Full play with task summary and tasks_list
- **PlayCreateSerializer**: For creating plays
- **TaskSummarySerializer**: Aggregated task counts (ok/changed/failed)
- **TaskSerializer**: Individual task with status and failure message

### Current API Endpoints

The backend uses Django REST Framework with ViewSets:
- `LogViewSet`: Create and retrieve logs with nested hosts and plays
- `PlayViewSet`: Access play-related operations including task listing

#### Logs

**POST** `/api/logs/`
- Upload and parse a new Ansible log
- Request body: `{ "title": "string", "raw_content": "string" }`
- Auto-detects log format (raw stdout or timestamped)
- Creates Log, Host, and Play entities from parsed data
- Returns 201 with full log data on success
- Returns 500 with detailed error on parsing failure

**Example Request:**
```json
{
  "title": "Production Deploy 2024-01-15",
  "raw_content": "PLAY [Setup Web Server] ***...\nPLAY RECAP ***..."
}
```

**GET** `/api/logs/{id}/`
- Retrieve a specific log with all hosts and plays
- Uses `prefetch_related` for optimized nested queries
- Response includes nested hosts with their plays (without individual task details)
- Use `/api/plays/{id}/tasks/` to get task details for a specific play

**Example Response:**
```json
{
  "id": "uuid-string",
  "title": "Deployment Log",
  "uploaded_at": "2024-01-15T10:30:00Z",
  "hosts": [
    {
      "id": "uuid-string",
      "hostname": "web-01.example.com",
      "plays": [
        {
          "id": "uuid-string",
          "name": "Setup Web Server",
          "date": "2024-01-15T10:30:00Z",
          "status": "ok",
          "tasks": {
            "ok": 10,
            "changed": 3,
            "failed": 0
          },
          "line_number": 1,
          "order": 0
        }
      ]
    }
  ],
  "host_count": 1
}
```

**GET** `/api/logs/{id}/hosts/`
- List all hosts for a specific log
- Custom action endpoint on the LogViewSet
- Returns hosts with their plays (without log metadata)

**Example Response:**
```json
[
  {
    "id": "uuid-string",
    "hostname": "web-01.example.com",
    "plays": [
      {
        "id": "uuid-string",
        "name": "Setup Web Server",
        "date": "2024-01-15T10:30:00Z",
        "status": "changed",
        "tasks": {
          "ok": 8,
          "changed": 5,
          "failed": 0
        },
        "line_number": 1,
        "order": 0
      }
    ]
  }
]
```

#### Plays

**GET** `/api/plays/{id}/tasks/`
- List all tasks for a specific play
- Supports filtering by task status via query parameter
- Returns tasks ordered by execution order

**Query Parameters:**
- `status` (optional): Filter by task status. Valid values: `ok`, `changed`, `failed`, `fatal`, `skipping`, `unreachable`, `ignored`, `rescued`
  - **Note:** Filtering by `failed` returns both `failed` and `fatal` tasks

**Response Codes:**
- `200 OK`: List of tasks returned successfully
- `400 Bad Request`: Invalid status parameter (includes valid options in response)
- `404 Not Found`: Play with given UUID does not exist

**Example Request:**
```bash
# Get all tasks for a play
GET /api/plays/550e8400-e29b-41d4-a716-446655440000/tasks/

# Get only failed tasks
GET /api/plays/550e8400-e29b-41d4-a716-446655440000/tasks/?status=failed
```

**Example Response (200):**
```json
[
  {
    "id": "uuid-string",
    "name": "Gathering Facts",
    "order": 0,
    "line_number": 3,
    "status": "ok",
    "failure_message": null
  },
  {
    "id": "uuid-string",
    "name": "Install nginx",
    "order": 1,
    "line_number": 7,
    "status": "changed",
    "failure_message": null
  }
]
```

**Example Error Response (400 - Invalid status):**
```json
{
  "error": "Invalid status 'invalid'",
  "valid_statuses": ["ok", "changed", "failed", "fatal", "skipping", "unreachable", "ignored", "rescued"]
}
```

### Log Parser Service

The `LogParserService` in [backend/api/services/log_parser.py](backend/api/services/log_parser.py) handles parsing Ansible output.

**Supported Formats:**
- **Raw stdout**: Direct output from `ansible-playbook` command (starts with `PLAY [...]`)
- **Timestamped logs**: Log files with timestamp prefix (`YYYY-MM-DD HH:MM:SS,mmm | ...`)

**Parsing Process:**
1. Auto-detect format based on first line
2. Parse using `ansible-output-parser` library
3. Extract hosts from PLAY RECAP section
4. Extract play names with line numbers
5. Extract tasks with per-host status and failure messages
6. Determine status per host (failed > changed > ok)

**Data Classes:**
- `ParsedHost`: hostname, ok, changed, failed, unreachable, skipped, rescued, ignored
- `ParsedPlay`: name, order, line_number
- `ParsedTask`: name, order, play_name, line_number, results (list of ParsedTaskResult)
- `ParsedTaskResult`: hostname, status (ok/changed/failed/fatal/skipping/unreachable/ignored/rescued), message
- `ParseResult`: success, hosts, plays, tasks, timestamp, error details

### Django Admin Interface

Access the admin at `http://localhost:8000/admin/` after creating a superuser.

**LogAdmin Features:**
- List view: title, uploaded_at, host count, total plays, failure status badge
- Filters: by date, has failures
- Search: by title, hostname
- Inline: view/edit hosts directly
- Custom action: "Test Log Submission" page for parsing logs

**HostAdmin Features:**
- List view: hostname, log title, play count, status summary badges, latest play date
- Filters: by log, date, play status (failed/changed/ok)
- Search: by hostname, log title
- Inline: view/edit plays directly

**PlayAdmin Features:**
- List view: name, hostname, log title, date, status badge, task summary, total tasks
- Filters: by status, date, host, log, has failed tasks, task count range
- Search: by name, hostname, log title
- Inline: view/edit tasks directly
- Fieldsets: organized into Play Information, Task Summary, Metadata sections

**TaskAdmin Features:**
- List view: name, play name, hostname, order, status badge, has error indicator
- Filters: by status, log, host
- Search: by task name, play name, hostname
- Fieldsets: organized into Task Information, Execution Result, Metadata sections
- Color-coded status badges for all task statuses (ok/changed/failed/fatal/skipped/unreachable/ignored/rescued)

**Custom Admin Filters:**
- `HasFailuresFilter`: Filter logs by whether they contain failed plays
- `PlayStatusFilter`: Filter hosts by play status composition
- `HasFailedTasksFilter`: Filter plays by failed task presence
- `TaskCountRangeFilter`: Filter plays by total task count (0-5, 6-10, 11-20, 20+)

**Test Submission Page:**
- URL: `/admin/api/log/submit-test/`
- Form to paste raw Ansible log content
- Shows parsing errors with traceback on failure
- Shows created log summary on success with link to view

### Current Limitations
- Log list endpoint not yet implemented (`GET /api/logs/`)
- Limited filtering (only task status filtering on `/api/plays/{id}/tasks/`)
- No log upload UI in frontend (must use admin or API directly)
- No authentication or user management
- No real-time updates

## Future Iterations

### v0.5.0 - Frontend Enhancements (Next)
- **Log Upload UI**: Form to submit Ansible logs from frontend
- **Log List Page**: Display all logs with navigation
- **Error Handling**: Display parsing errors to users
- **Loading States**: Skeleton loaders during API calls

### v0.6.0 - Enhanced API
- `GET /api/logs/` - List all logs with pagination
- `GET /api/hosts/` - List all hosts across logs
- `GET /api/plays/` - List all plays with filtering
- Search and filter capabilities on API endpoints
- Export functionality (JSON, CSV formats)

### v0.7.0 - Enhanced UI Features
- Task search and filtering in UI
- Jump to line number in raw log view
- Improved error handling and user feedback

### v0.8.0+ - Advanced Features
- User authentication and authorization (JWT or session-based)
- Multi-user support with role-based access control
- Real-time updates with WebSocket support
- Email/Slack notifications for play failures
- Dashboard with analytics and trends
- Play history and comparison views
- Dark/Light mode toggle
- Customizable views and user preferences
- HTTPS termination with Let's Encrypt
- Health checks and monitoring
- Log aggregation and analytics

## File Organization

### Root Files
- [CLAUDE.md](CLAUDE.md) - This project documentation file
- [.gitignore](.gitignore) - Git ignore patterns (frontend, backend, Python)
- [Dockerfile](Dockerfile) - Multi-stage Docker build configuration
- [docker-compose.yml](docker-compose.yml) - Docker Compose orchestration
- [.dockerignore](.dockerignore) - Docker build context exclusions
- [.env.production](.env.production) - Production environment variables template

### Frontend Configuration Files
- [frontend/package.json](frontend/package.json) - NPM dependencies and scripts
- [frontend/vite.config.ts](frontend/vite.config.ts) - Vite build configuration
- [frontend/eslint.config.js](frontend/eslint.config.js) - ESLint configuration with TypeScript support
- [frontend/tsconfig.json](frontend/tsconfig.json) - TypeScript project references
- [frontend/tsconfig.app.json](frontend/tsconfig.app.json) - App TypeScript config
- [frontend/tsconfig.node.json](frontend/tsconfig.node.json) - Node scripts TypeScript config
- [frontend/tailwind.config.js](frontend/tailwind.config.js) - Tailwind CSS configuration
- [frontend/postcss.config.js](frontend/postcss.config.js) - PostCSS plugins

### Frontend Source Files
- [frontend/src/main.tsx](frontend/src/main.tsx) - React application entry point
- [frontend/src/App.tsx](frontend/src/App.tsx) - Main application component with React Router
- [frontend/src/index.css](frontend/src/index.css) - Global styles and Tailwind directives
- [frontend/src/vite-env.d.ts](frontend/src/vite-env.d.ts) - Vite environment type declarations
- [frontend/src/types/ansible.ts](frontend/src/types/ansible.ts) - TypeScript type definitions (Host, Play, Task, TaskSummary)
- [frontend/src/services/api.ts](frontend/src/services/api.ts) - Backend API client (fetchLog, fetchTasks)
- [frontend/src/pages/LogPage.tsx](frontend/src/pages/LogPage.tsx) - Log detail page with hosts grid
- [frontend/src/components/CollapsibleTaskSection.tsx](frontend/src/components/CollapsibleTaskSection.tsx) - Expandable task list with lazy loading and JSON syntax highlighting
- [frontend/src/components/PlayCard.tsx](frontend/src/components/PlayCard.tsx) - Individual play card with collapsible task sections
- [frontend/src/components/PlayHeader.tsx](frontend/src/components/PlayHeader.tsx) - (Legacy) Play title and date component
- [frontend/src/components/ServerCard.tsx](frontend/src/components/ServerCard.tsx) - Host card displaying multiple plays
- [frontend/src/components/StatusBadge.tsx](frontend/src/components/StatusBadge.tsx) - Status indicator badge with expand support

### Backend Configuration Files
- [backend/pyproject.toml](backend/pyproject.toml) - Poetry dependencies and project metadata
- [backend/manage.py](backend/manage.py) - Django management command-line utility
- [backend/README.md](backend/README.md) - Backend-specific documentation
- [backend/.env.example](backend/.env.example) - Environment variables template

### Backend Source Files
- [backend/ansible_ui/settings.py](backend/ansible_ui/settings.py) - Django settings (apps, middleware, CORS, DRF)
- [backend/ansible_ui/urls.py](backend/ansible_ui/urls.py) - Root URL configuration
- [backend/ansible_ui/wsgi.py](backend/ansible_ui/wsgi.py) - WSGI application
- [backend/ansible_ui/asgi.py](backend/ansible_ui/asgi.py) - ASGI application
- [backend/api/views.py](backend/api/views.py) - API view implementations (LogViewSet, PlayViewSet)
- [backend/api/urls.py](backend/api/urls.py) - API URL routing
- [backend/api/models.py](backend/api/models.py) - Database models (Log, Host, Play, Task)
- [backend/api/serializers.py](backend/api/serializers.py) - DRF serializers for all models
- [backend/api/admin.py](backend/api/admin.py) - Django admin configuration with custom filters
- [backend/api/tests.py](backend/api/tests.py) - Test cases (future)
- [backend/api/migrations/](backend/api/migrations/) - Database migration files

### Backend Services
- [backend/api/services/log_parser.py](backend/api/services/log_parser.py) - Ansible log parsing service

### Backend Admin Templates
- [backend/api/templates/admin/api/log/change_list.html](backend/api/templates/admin/api/log/change_list.html) - Custom log list with test submission link
- [backend/api/templates/admin/api/log/submit_test.html](backend/api/templates/admin/api/log/submit_test.html) - Test log submission form

### Docker Configuration Files
- [docker/entrypoint.api.sh](docker/entrypoint.api.sh) - API container startup script (waits for DB, runs migrations, starts gunicorn)
- [docker/nginx.conf](docker/nginx.conf) - nginx configuration for reverse proxy and static file serving

## Design Decisions

### Why Vite over Create React App?
- Significantly faster dev server startup
- Hot Module Replacement (HMR) is more responsive
- Smaller bundle sizes with better tree-shaking
- Native ESM support
- Better TypeScript integration

### Why Dark Mode First?
- Terminal-friendly aesthetic aligns with DevOps workflows
- Reduces eye strain for users monitoring systems
- Modern, professional appearance
- Better contrast for status colors

### Why Tailwind CSS?
- Rapid prototyping with utility classes
- Consistent design system
- Smaller CSS bundle (only used classes)
- No CSS naming conflicts
- Easy responsive design

### Why Lucide React?
- Lightweight icon library
- Consistent design language
- Tree-shakeable (only import icons you use)
- Active maintenance and updates
- Better than Font Awesome for React projects

### Why Django REST Framework?
- Mature, production-ready framework for building APIs
- Excellent serialization and validation tools
- Built-in browsable API for development
- Strong authentication and permissions system
- Large ecosystem and community support
- Works seamlessly with Django ORM

### Why Poetry over pip/requirements.txt?
- Deterministic dependency resolution
- Automatic virtual environment management
- Modern pyproject.toml standard
- Separates development and production dependencies
- Lockfile ensures reproducible builds
- Better dependency conflict resolution

### Why ansible-output-parser?
- Purpose-built library for parsing Ansible output
- Handles both raw stdout and timestamped log formats
- Extracts PLAY RECAP data with task counts per host
- Parses play names and structure
- Maintained library with active development

### Why Poe the Poet?
- Integrated task runner for pyproject.toml
- Combines multiple commands into single tasks
- Supports sequential and parallel execution
- Clean interface: `poetry run poe lint` vs multiple commands
- Configured alongside Poetry dependencies

### Why python-decouple?
- Clean separation of configuration from code
- Supports both environment variables and `.env` files
- Type casting with `cast` parameter (bool, int, Csv)
- Secure defaults for development
- Production-ready configuration pattern
- No code changes needed between environments

### Why Docker Multi-stage Builds?
- **Optimized image sizes**: Each stage only contains what's needed
- **Build caching**: Faster rebuilds by caching layers
- **Security**: Production images don't include build tools
- **Separation of concerns**: Frontend, backend, and runtime are isolated
- **Reference consistency**: Follows `platform_api` pattern with Rocky Linux 9
- **Production ready**: gunicorn + nginx + PostgreSQL stack

### ESLint Configuration
The project uses modern ESLint flat config (eslint.config.js) with:
- **TypeScript ESLint**: Type-aware linting rules
- **React Hooks Plugin**: Ensures hooks are used correctly
- **React Refresh Plugin**: Validates Fast Refresh compatibility
- **Recommended Rulesets**: Industry-standard best practices

ESLint helps maintain code quality by:
- Catching potential bugs before runtime
- Enforcing consistent code style
- Identifying unused variables and imports
- Validating React patterns and TypeScript types

Run `npm run lint` before committing to ensure code quality.

## Quality Assurance

### Code Quality Checks
The project includes comprehensive code quality tooling:

**ESLint Configuration**
- Modern flat config format (eslint.config.js)
- TypeScript-aware linting with typescript-eslint
- React Hooks rules enforcement
- React Refresh compatibility checks

**TypeScript Strict Mode**
- Strict type checking enabled
- No unused locals or parameters allowed
- No fallthrough cases in switch statements
- No unchecked side effect imports

**Running Frontend Quality Checks**
```bash
# Navigate to frontend directory
cd frontend

# Run ESLint
npm run lint

# Run TypeScript compiler check (without emitting files)
npx tsc -b --noEmit

# Run both checks in CI/CD
npm run lint && npx tsc -b --noEmit
```

**Running Backend Quality Checks**
```bash
# Navigate to backend directory
cd backend

# Run all lint checks (autoflake, flake8, black)
poetry run poe lint

# Auto-fix lint issues
poetry run poe fix

# Individual checks
poetry run poe lint-check     # Check unused imports/variables
poetry run poe flake8-check   # Style checks
poetry run poe black-check    # Format check
```

**Current Status**: ✅ All checks passing
- Zero ESLint errors or warnings (frontend)
- Zero TypeScript type errors (frontend)
- Zero flake8/black issues (backend)
- Production-ready codebase

## Contributing

When extending this project, follow these guidelines:

### Frontend
1. **Maintain Type Safety**: Always use TypeScript types from `src/types/`
2. **Component Reusability**: Create small, focused components
3. **Consistent Styling**: Use Tailwind utilities, avoid custom CSS
4. **Dark Mode First**: Design for dark mode, then adapt if light mode is added
5. **Responsive Design**: Test on mobile, tablet, and desktop viewports
6. **Accessibility**: Use semantic HTML and ARIA labels where appropriate

### Backend
1. **Run Linting**: Always run `poetry run poe lint` before committing
2. **Auto-fix Issues**: Use `poetry run poe fix` to auto-format code
3. **Service Layer**: Put business logic in `api/services/`, keep views thin
4. **Type Hints**: Use Python type hints for function signatures
5. **Django Admin**: Leverage admin interface for data inspection and testing
6. **Migrations**: Create migrations for any model changes
7. **Query Optimization**: Use `select_related` and `prefetch_related` for nested queries

## Troubleshooting

### Frontend Issues

**Port Already in Use**
If port 5173 is occupied:
```bash
npm run dev -- --port 3000
```

**TypeScript Errors**
Ensure all dependencies are installed:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Tailwind Styles Not Applying**
Check that [frontend/src/index.css](frontend/src/index.css) is imported in [frontend/src/main.tsx](frontend/src/main.tsx) and contains the Tailwind directives.

### Backend Issues

**Port 8000 Already in Use**
Specify a different port:
```bash
poetry run python manage.py runserver 8080
```
Remember to update CORS settings if you change the port.

**Poetry Virtual Environment Issues**
Remove and recreate the virtual environment:
```bash
cd backend
poetry env remove python3.12
poetry install
```

**CORS Errors**
If frontend can't connect to backend:
1. Verify backend is running on `http://localhost:8000`
2. Check `CORS_ALLOWED_ORIGINS` in [backend/ansible_ui/settings.py](backend/ansible_ui/settings.py)
3. Ensure `corsheaders` middleware is configured

**Database Migration Errors**
Reset the database (development only):
```bash
cd backend
rm db.sqlite3
poetry run python manage.py migrate
```

**Environment Variable Issues**
If settings aren't being read from `.env`:
1. Ensure `.env` file is in the `backend/` directory (same level as `manage.py`)
2. Check for typos in variable names
3. Restart the Django server after changing `.env`

**Production Database Connection Errors**
When `DJANGO_PROD=True`:
1. Verify all `DB_*` environment variables are set
2. Check PostgreSQL is running and accessible
3. Verify database credentials are correct
4. Ensure the database exists: `createdb ansible_ui`

### Docker Issues

**Build Failures**
If `docker-compose build` fails:
1. Check Docker daemon is running: `docker ps`
2. Ensure sufficient disk space: `docker system df`
3. Clear build cache: `docker builder prune`
4. Check `package-mode = false` has been removed from `backend/pyproject.toml`

**Container Won't Start**
If containers exit immediately:
1. Check logs: `docker-compose logs api` or `docker-compose logs web`
2. Verify `.env` file exists and has correct values
3. Check port 80 isn't already in use: `lsof -i :80`
4. Verify PostgreSQL is healthy: `docker-compose ps db`

**Database Connection Issues**
If API can't connect to database:
1. Ensure `DB_HOSTNAME=db` (matches service name in docker-compose.yml)
2. Check database is running: `docker-compose ps db`
3. View database logs: `docker-compose logs db`
4. Verify environment variables match: `docker-compose exec api env | grep DB_`

**Static Files Not Loading**
If CSS/JS don't load:
1. Verify `collectstatic` ran: `docker-compose logs api | grep collectstatic`
2. Check nginx config: `docker-compose exec web cat /etc/nginx/conf.d/nginx.conf`
3. Rebuild web service: `docker-compose build web`

**Permission Denied on entrypoint.api.sh**
If you see "permission denied" errors:
```bash
chmod +x docker/entrypoint.api.sh
docker-compose build api
```

## License

This project is for internal use. Backend integration and production deployment details will be added in future iterations.
