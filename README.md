# Notepad

A web-based note-taking application with a React frontend, FastAPI backend, and PostgreSQL database.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Getting Started

1. **Clone the repo and create your environment file:**

   ```bash
   cp .env.example .env
   ```

2. **Start all services:**

   ```bash
   docker compose up --build -d
   ```

3. **Run database migrations:**

   ```bash
   docker compose exec backend alembic upgrade head
   ```

4. **Open the app:**

   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API docs (Swagger): http://localhost:8000/docs

## Running Tests

```bash
docker compose exec backend pytest -v
```

## Useful Commands

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start all services in background |
| `docker compose down` | Stop all services |
| `docker compose logs backend --tail=50` | View backend logs |
| `docker compose logs frontend --tail=50` | View frontend logs |
| `docker compose up --build -d backend` | Rebuild and restart backend |
| `docker compose exec backend alembic revision --autogenerate -m "description"` | Generate a new migration |
| `docker compose exec backend alembic upgrade head` | Apply all migrations |
| `docker compose exec backend alembic downgrade -1` | Rollback last migration |
| `docker compose exec db psql -U notepad -d notepad` | Open a PostgreSQL shell |

## Project Structure

```
notepad/
├── frontend/               # React (Vite + TypeScript)
│   ├── src/
│   │   ├── components/     # Sidebar, NoteList, NoteEditor, Search
│   │   ├── hooks/
│   │   ├── services/       # API client
│   │   ├── store/          # State management (Zustand)
│   │   ├── types/          # TypeScript interfaces
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── backend/                # Python (FastAPI)
│   ├── app/
│   │   ├── api/            # Route handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # Business logic
│   │   ├── core/           # Config, security, database
│   │   └── main.py
│   ├── alembic/            # Database migrations
│   ├── tests/              # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── .env
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, TypeScript, TipTap, Zustand |
| Backend | Python, FastAPI, SQLAlchemy, asyncpg |
| Database | PostgreSQL 16 |
| Auth | JWT (access + refresh tokens), bcrypt |
| Migrations | Alembic |
| Testing | pytest, pytest-asyncio, httpx |
