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
- **ESLint**: Code linting and quality enforcement

### Backend
- **Python 3.12+**: Modern Python with performance improvements
- **Django 5.2**: High-level web framework
- **Django REST Framework 3.16**: Powerful toolkit for building Web APIs
- **Poetry**: Dependency management and packaging
- **SQLite**: Development database (PostgreSQL for production)
- **django-cors-headers**: CORS support for frontend communication
- **ansible-output-parser**: Library for parsing Ansible playbook output
- **Poe the Poet**: Task runner for linting and code quality commands

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
│   │   ├── settings.py   # Django settings (CORS, DRF)
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
│   └── README.md         # Backend documentation
│
├── CLAUDE.md             # This file
└── .gitignore            # Git ignore patterns
```

### Frontend Component Structure

```
frontend/src/
├── components/
│   ├── PlayCard.tsx        # Displays individual play with task summaries
│   ├── PlayHeader.tsx      # (Legacy) Displays play title and execution date
│   ├── ServerCard.tsx      # Host card displaying multiple plays
│   └── StatusBadge.tsx     # Reusable status indicator badge
├── types/
│   └── ansible.ts          # TypeScript type definitions
├── App.tsx                 # Main application component
├── main.tsx                # React app entry point
└── index.css               # Global styles and Tailwind directives
```

### Data Model

The application uses a hierarchical data structure to organize Ansible execution data:

```
Log (uploaded Ansible log file)
 └── Host (servers in the log)
      └── Play (play executions on the host)
           └── TaskSummary (task counts: ok/changed/failed)
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
- Three StatusBadge components showing task counts (OK/Changed/Failed)
- Compact design suitable for multiple plays per host

#### StatusBadge
- Reusable component for displaying status counts
- Color-coded backgrounds with semi-transparent overlays
- Border styling for definition
- Flex layout with label and count

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

### Mock Data

The first iteration uses hardcoded mock data in [frontend/src/App.tsx](frontend/src/App.tsx):
- 5 example hosts with realistic hostnames (web-01, web-02, db-01, lb-01, cache-01)
- Each host has 1-3 plays with descriptive names
- Mix of OK, Changed, and Failed play statuses
- Varied task counts per play (5-18 tasks)
- Execution timestamps showing relative times for each play

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

### v0.3.0 - Log Parsing & Admin Interface (Current)
- **Ansible Log Parser Service**: Auto-detects and parses both raw stdout and timestamped log formats
- **POST `/api/logs/` Endpoint**: Upload and parse Ansible logs via API
- **Django Admin Interface**: Full admin panel with custom features
- **Admin Filters**: Custom filters for failures, play status, task counts
- **Admin Inlines**: View hosts and plays inline when editing logs
- **Test Submission Page**: Custom admin view for testing log parsing
- **Play Ordering**: Line number and order fields for accurate play sequencing
- **Poe Task Runner**: Integrated linting commands (autoflake, flake8, black)

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
- Database indexes for efficient querying

### Available Serializers

- **LogSerializer**: Full log with nested hosts
- **LogListSerializer**: Lightweight log listing
- **LogCreateSerializer**: For uploading new logs
- **HostSerializer**: Full host with nested plays
- **HostListSerializer**: Lightweight host listing
- **PlaySerializer**: Full play with task summary
- **PlayCreateSerializer**: For creating plays
- **TaskSummarySerializer**: Task counts (ok/changed/failed)

### Current API Endpoints

The backend uses Django REST Framework with a `LogViewSet` that provides create and retrieve access to logs.

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
- Response includes nested hosts with their plays

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
5. Determine status per host (failed > changed > ok)

**Data Classes:**
- `ParsedHost`: hostname, ok, changed, failed, unreachable, skipped, rescued, ignored
- `ParsedPlay`: name, order, line_number
- `ParseResult`: success, hosts, plays, timestamp, error details

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
- Fieldsets: organized into Play Information, Task Summary, Metadata sections

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
- Frontend still uses mock data (backend integration in progress)
- Log list endpoint not yet implemented (`GET /api/logs/`)
- No filtering or search capabilities on API endpoints
- No authentication or user management
- No real-time updates

## Future Iterations

### v0.4.0 - Frontend Integration (Next)
- **Frontend API Integration**: Replace mock data with API calls
- **Log Upload UI**: Form to submit Ansible logs from frontend
- **Error Handling**: Display parsing errors to users
- **Loading States**: Skeleton loaders during API calls

### v0.5.0 - Enhanced API
- `GET /api/logs/` - List all logs with pagination
- `GET /api/hosts/` - List all hosts across logs
- `GET /api/plays/` - List all plays with filtering
- Search and filter capabilities on API endpoints
- Export functionality (JSON, CSV formats)

### v0.6.0 - Enhanced UI Features
- Detailed task-level information display
- Expandable server cards with full task details
- Improved error handling and user feedback

### v0.7.0+ - Advanced Features
- User authentication and authorization (JWT or session-based)
- Multi-user support with role-based access control
- Real-time updates with WebSocket support
- Email/Slack notifications for play failures
- Dashboard with analytics and trends
- Play history and comparison views
- Dark/Light mode toggle
- Customizable views and user preferences
- PostgreSQL migration for production
- Docker containerization

## File Organization

### Root Files
- [CLAUDE.md](CLAUDE.md) - This project documentation file
- [.gitignore](.gitignore) - Git ignore patterns (frontend, backend, Python)

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
- [frontend/src/App.tsx](frontend/src/App.tsx) - Main application component with mock host data
- [frontend/src/index.css](frontend/src/index.css) - Global styles and Tailwind directives
- [frontend/src/vite-env.d.ts](frontend/src/vite-env.d.ts) - Vite environment type declarations
- [frontend/src/types/ansible.ts](frontend/src/types/ansible.ts) - TypeScript type definitions (Host, Play, TaskSummary)
- [frontend/src/components/PlayCard.tsx](frontend/src/components/PlayCard.tsx) - Individual play card with task summaries
- [frontend/src/components/PlayHeader.tsx](frontend/src/components/PlayHeader.tsx) - (Legacy) Play title and date component
- [frontend/src/components/ServerCard.tsx](frontend/src/components/ServerCard.tsx) - Host card displaying multiple plays
- [frontend/src/components/StatusBadge.tsx](frontend/src/components/StatusBadge.tsx) - Status indicator badge

### Backend Configuration Files
- [backend/pyproject.toml](backend/pyproject.toml) - Poetry dependencies and project metadata
- [backend/manage.py](backend/manage.py) - Django management command-line utility
- [backend/README.md](backend/README.md) - Backend-specific documentation

### Backend Source Files
- [backend/ansible_ui/settings.py](backend/ansible_ui/settings.py) - Django settings (apps, middleware, CORS, DRF)
- [backend/ansible_ui/urls.py](backend/ansible_ui/urls.py) - Root URL configuration
- [backend/ansible_ui/wsgi.py](backend/ansible_ui/wsgi.py) - WSGI application
- [backend/ansible_ui/asgi.py](backend/ansible_ui/asgi.py) - ASGI application
- [backend/api/views.py](backend/api/views.py) - API view implementations (LogViewSet)
- [backend/api/urls.py](backend/api/urls.py) - API URL routing
- [backend/api/models.py](backend/api/models.py) - Database models (Log, Host, Play)
- [backend/api/serializers.py](backend/api/serializers.py) - DRF serializers for all models
- [backend/api/admin.py](backend/api/admin.py) - Django admin configuration with custom filters
- [backend/api/tests.py](backend/api/tests.py) - Test cases (future)
- [backend/api/migrations/](backend/api/migrations/) - Database migration files

### Backend Services
- [backend/api/services/log_parser.py](backend/api/services/log_parser.py) - Ansible log parsing service

### Backend Admin Templates
- [backend/api/templates/admin/api/log/change_list.html](backend/api/templates/admin/api/log/change_list.html) - Custom log list with test submission link
- [backend/api/templates/admin/api/log/submit_test.html](backend/api/templates/admin/api/log/submit_test.html) - Test log submission form

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

## License

This project is for internal use. Backend integration and production deployment details will be added in future iterations.
