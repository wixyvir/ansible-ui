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
│   │   └── serializers.py # DRF serializers
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
  date: string;         // Execution timestamp
  status: PlayStatus;   // Play status (ok/changed/failed)
  tasks: TaskSummary;   // Task execution counts for this play
}
```

**Backend Model** (Django):
- `host`: ForeignKey to Host
- `name`: CharField - Play name
- `date`: DateTimeField - Execution timestamp
- `status`: CharField with choices (ok/changed/failed)
- `tasks_ok`, `tasks_changed`, `tasks_failed`: IntegerFields
- `tasks` property returns TaskSummary dict for API serialization

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
- `poetry run black .` - Format code (future)
- `poetry run flake8` - Lint code (future)

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

### v0.2.0 - Backend Foundation (Current)
- **Django REST Framework Backend**: Python 3.12 with Django 5.2
- **Poetry Dependency Management**: Modern Python packaging and dependency resolution
- **API Structure**: RESTful API architecture with `/api/` prefix
- **Database Models**: Log, Host, and Play models implemented
- **DRF Serializers**: Complete serializers for all models with frontend compatibility
- **CORS Configuration**: Frontend-backend communication enabled
- **SQLite Database**: Initialized with Django migrations
- **Development Ready**: Comprehensive documentation and setup guides

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
- Fields: `name`, `date`, `status`, `tasks_ok`, `tasks_changed`, `tasks_failed`
- ForeignKey to Host
- Status choices: ok, changed, failed
- `tasks` property returns TaskSummary dict

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

The backend uses Django REST Framework with a `LogViewSet` that provides read-only access to logs.

#### Logs

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
          }
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
        }
      }
    ]
  }
]
```

### Current Limitations
- Frontend still uses mock data (backend integration in progress)
- Log list endpoint not yet implemented (`GET /api/logs/`)
- Log creation/upload endpoint not yet implemented (`POST /api/logs/`)
- No Ansible log parsing yet
- No file upload functionality
- No filtering or search capabilities
- No authentication or user management
- No real-time updates

## Future Iterations

### v0.2.x - Backend API Endpoints (Next)
- **Remaining API Endpoints**:
  - `GET /api/logs/` - List all logs (not yet implemented)
  - `POST /api/logs/` - Upload new log file (not yet implemented)
  - `GET /api/hosts/` - List all hosts
  - `GET /api/hosts/{id}/` - Get host details with plays
  - `GET /api/plays/` - List all plays with filtering
  - `GET /api/plays/{id}/` - Get play details
- **Ansible Log Parsing**: Process JSON output from ansible-playbook
- **Frontend Integration**: Replace mock data with API calls
- **Log Parser**: Parse Ansible JSON output and populate database

### v0.3.0 - Enhanced Features
- Historical play logs with pagination
- Search and filter capabilities (by hostname, status, date)
- Detailed task-level information display
- Expandable server cards with full task details
- Export functionality (JSON, CSV formats)
- Improved error handling and user feedback

### v0.4.0+ - Advanced Features
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
- [backend/api/tests.py](backend/api/tests.py) - Test cases (future)
- [backend/api/migrations/](backend/api/migrations/) - Database migration files

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

**Running Quality Checks**
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

**Current Status**: ✅ All checks passing
- Zero ESLint errors or warnings
- Zero TypeScript type errors
- Production-ready codebase

## Contributing

When extending this project, follow these guidelines:

1. **Maintain Type Safety**: Always use TypeScript types from `src/types/`
2. **Component Reusability**: Create small, focused components
3. **Consistent Styling**: Use Tailwind utilities, avoid custom CSS
4. **Dark Mode First**: Design for dark mode, then adapt if light mode is added
5. **Responsive Design**: Test on mobile, tablet, and desktop viewports
6. **Accessibility**: Use semantic HTML and ARIA labels where appropriate

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
