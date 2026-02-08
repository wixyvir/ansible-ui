# Ansibeau

A modern React web application that displays comprehensive views of Ansible Play execution results with a professional, clean, and elegant dark mode interface.

## What it does

This project displays a comprehensive view of Ansible execution results organized by host, featuring:
- Host cards showing multiple plays executed on each server
- Individual play cards with task summaries (OK/Changed/Failed)
- Visual status indicators for hosts and plays
- Responsive grid layout with nested card hierarchy
- Professional dark mode design optimized for DevOps workflows

## Dev Quick Setup

Get up and running in under 2 minutes:

### Prerequisites
- Node.js 18+ and npm installed

### Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Run code quality checks
npm run lint

# 3. Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Available Commands

```bash
npm run dev      # Start dev server with hot reload
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint checks
```

### Verify Setup

Run all quality checks to ensure everything is working:

```bash
npm run lint && npx tsc -b --noEmit
```

Expected output: ✅ All checks passing

## Technology Stack

- **React 18** with TypeScript
- **Vite** for blazing-fast development
- **Tailwind CSS** for styling
- **ESLint** for code quality
- **Lucide React** for icons

## Documentation

See [CLAUDE.md](CLAUDE.md) for comprehensive documentation including:
- Architecture and component design
- Data models and TypeScript types
- Development workflow
- Future roadmap

## Project Structure

```
src/
├── components/
│   ├── PlayCard.tsx        # Individual play with task summaries
│   ├── PlayHeader.tsx      # (Legacy) Title and date display
│   ├── ServerCard.tsx      # Host card with multiple plays
│   └── StatusBadge.tsx     # Status indicator badge
├── types/
│   └── ansible.ts          # TypeScript interfaces (Host, Play, TaskSummary)
├── App.tsx                 # Main application
└── main.tsx                # Entry point
```

## Current Version: v0.1.0

First iteration with mock data. Backend integration planned for v0.2.0.
