# Notepad — Application Specification

## Overview

**Notepad** is a web-based note-taking application that allows users to create, organize, and manage notes through a clean, intuitive interface. Notes are stored in the cloud and accessible across multiple devices and browsers.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React (Vite) |
| Editor | TipTap (rich text / markdown WYSIWYG) |
| Backend | Python / FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async with asyncpg) |
| Auth | Email/password (JWT-based) |

---

## Phase 1 — Core Features

### Authentication

- Email and password registration and login
- JWT-based session management (access token + refresh token)
- Password hashing with bcrypt
- Protected API routes via auth middleware
- Logout / session invalidation
- Password reset via email (optional, recommended)

### Note Management

#### Creating & Editing Notes
- Each note has a **title** and **body**
- Body content is edited via a **TipTap** rich-text editor with markdown support
- Supported formatting: bold, italic, strikethrough, headings (H1–H3), bullet lists, numbered lists, code blocks, blockquotes, horizontal rules, links
- **Auto-save** — notes save automatically as the user types (debounced, ~1 second after last keystroke)
- Manual save option also available (Cmd/Ctrl+S)
- No note size limit
- Notes store the following metadata:
  - `id` (UUID)
  - `title` (string)
  - `body` (stored as TipTap JSON or HTML)
  - `folder_id` (foreign key, nullable for root-level notes)
  - `is_starred` (boolean, default false)
  - `is_trashed` (boolean, default false)
  - `trashed_at` (timestamp, nullable)
  - `created_at` (timestamp)
  - `updated_at` (timestamp)
  - `user_id` (foreign key)

#### Starring / Pinning
- Users can star/unstar notes
- Starred notes appear in the "Starred" virtual folder
- Starred notes also appear pinned to the top of their containing folder's note list

#### Deleting Notes
- Deleting a note moves it to **Trash** (soft delete: sets `is_trashed = true` and `trashed_at` to current time)
- Trash retains notes for **60 days**, after which they are permanently deleted (scheduled background job)
- Users can restore notes from Trash
- Users can permanently delete notes from Trash manually

### Folder System

#### Structure
- Notes are organized in a **nested folder hierarchy** (unlimited depth)
- Folders can contain both notes and sub-folders
- Folder data model:
  - `id` (UUID)
  - `name` (string)
  - `parent_id` (self-referencing foreign key, nullable for root-level folders)
  - `user_id` (foreign key)
  - `created_at` (timestamp)
  - `updated_at` (timestamp)
  - `sort_order` (integer, for ordering within parent)

#### Default / Virtual Folders
These are not stored in the database as folder records — they are virtual views:
- **All Notes** — displays every non-trashed note across all folders, sorted by last updated
- **Starred** — displays all starred, non-trashed notes
- **Trash** — displays all trashed notes with days remaining before permanent deletion

#### Folder Operations
- Create, rename, delete folders
- Deleting a folder moves all contained notes and sub-folders to Trash
- Move notes between folders via **drag and drop**
- Move folders via drag and drop (re-parenting)

### Search

- **Full-text search** across all non-trashed notes (title and body)
- Search bar accessible via keyboard shortcut (Cmd/Ctrl+K)
- Results displayed as a filterable list with note title, snippet preview, and folder location
- Search powered by PostgreSQL full-text search (`tsvector` / `tsquery`)

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New note | Cmd/Ctrl + N |
| Save note | Cmd/Ctrl + S |
| Search | Cmd/Ctrl + K |
| Delete note | Cmd/Ctrl + Backspace |
| Bold | Cmd/Ctrl + B |
| Italic | Cmd/Ctrl + I |
| Heading | Cmd/Ctrl + 1/2/3 |

---

## UI / Layout

### Desktop Layout (Primary)

Three-panel layout, similar to Apple Notes:

```
┌──────────────┬──────────────────┬──────────────────────────────┐
│              │                  │                              │
│   Sidebar    │    Note List     │       Note Editor            │
│              │                  │                              │
│  - All Notes │  - Note title    │  - Title field               │
│  - Starred   │  - Preview       │  - TipTap rich text editor   │
│  - Folders   │  - Date          │  - Auto-save indicator       │
│    - Nested  │  - Star icon     │  - Metadata (date, folder)   │
│  - Trash     │                  │                              │
│              │                  │                              │
│              │  [Search bar]    │                              │
│              │                  │                              │
└──────────────┴──────────────────┴──────────────────────────────┘
```

#### Sidebar (Left Panel)
- Virtual folders at top: All Notes, Starred, Trash
- User-created folder tree below with expand/collapse
- "New Folder" button
- Drag-and-drop support for reordering and nesting
- Active folder highlighted

#### Note List (Middle Panel)
- Shows notes in the currently selected folder
- Each note entry displays: title, body preview (first ~100 chars), last updated date, star indicator
- Starred notes pinned to top
- Sort by: last updated (default), created date, title (alphabetical)
- Search bar at top of panel

#### Note Editor (Right Panel)
- Note title as editable field at top
- TipTap WYSIWYG editor for body
- Formatting toolbar (can be toggled)
- Auto-save status indicator (e.g., "Saved" / "Saving...")
- Last updated timestamp displayed

### Mobile / Tablet Layout (Responsive)

- Single-panel view with navigation between views
- Sidebar accessible via hamburger menu
- Note list view → tap note → full-screen editor
- Notes are **viewable and editable** on mobile, but desktop is the primary design target
- Responsive breakpoints:
  - Desktop: ≥1024px (three-panel)
  - Tablet: 768–1023px (two-panel, sidebar collapsible)
  - Mobile: <768px (single panel)

---

## API Design

RESTful API with the following resource groups:

### Auth Endpoints
```
POST   /api/auth/register        — Create account
POST   /api/auth/login            — Login, return JWT
POST   /api/auth/refresh          — Refresh access token
POST   /api/auth/logout           — Invalidate session
```

### Notes Endpoints
```
GET    /api/notes                  — List notes (supports query params: folder_id, starred, trashed, search)
POST   /api/notes                  — Create note
GET    /api/notes/:id              — Get single note
PUT    /api/notes/:id              — Update note (title, body, folder_id, is_starred)
DELETE /api/notes/:id              — Soft delete (move to trash)
POST   /api/notes/:id/restore     — Restore from trash
DELETE /api/notes/:id/permanent    — Permanent delete
```

### Folders Endpoints
```
GET    /api/folders                — List all folders (returns tree structure)
POST   /api/folders                — Create folder
PUT    /api/folders/:id            — Update folder (name, parent_id, sort_order)
DELETE /api/folders/:id            — Delete folder (cascade to trash)
```

### Search Endpoint
```
GET    /api/search?q=<query>       — Full-text search across notes
```

---

## Database Schema

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| email | VARCHAR(255) | Unique, indexed |
| password_hash | VARCHAR(255) | bcrypt hash |
| created_at | TIMESTAMP | Default now() |
| updated_at | TIMESTAMP | Default now() |

### folders
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| name | VARCHAR(255) | Required |
| parent_id | UUID | FK → folders.id, nullable |
| user_id | UUID | FK → users.id |
| sort_order | INTEGER | Default 0 |
| created_at | TIMESTAMP | Default now() |
| updated_at | TIMESTAMP | Default now() |

### notes
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | Primary key |
| title | VARCHAR(500) | Default "Untitled" |
| body | TEXT | TipTap JSON content |
| folder_id | UUID | FK → folders.id, nullable |
| user_id | UUID | FK → users.id |
| is_starred | BOOLEAN | Default false |
| is_trashed | BOOLEAN | Default false |
| trashed_at | TIMESTAMP | Nullable |
| created_at | TIMESTAMP | Default now() |
| updated_at | TIMESTAMP | Default now() |
| search_vector | TSVECTOR | Auto-updated for full-text search |

### Indexes
- `notes.user_id` — filter by user
- `notes.folder_id` — filter by folder
- `notes.search_vector` — GIN index for full-text search
- `notes.is_trashed, notes.trashed_at` — for trash cleanup job
- `folders.user_id, folders.parent_id` — folder tree queries

---

## Background Jobs

- **Trash cleanup**: Runs daily, permanently deletes notes where `is_trashed = true` AND `trashed_at < now() - 60 days`. Can be implemented via a lightweight scheduler (APScheduler or similar) or a cron-triggered endpoint.

---

## Security Considerations

- All API routes (except auth) require valid JWT
- Users can only access their own notes and folders (enforce `user_id` filtering on all queries)
- Input sanitization on note content to prevent XSS
- Rate limiting on auth endpoints to prevent brute force
- CORS configuration for frontend origin
- HTTPS required in production

---

## Phase 2 — Future Enhancements

The following features are out of scope for Phase 1 but planned for future development:

- **Dark mode** — theme toggle with system preference detection
- **Export** — download notes as `.md` or `.txt` files
- **Image and file attachments** — upload and embed images/files in notes
- **Note sharing** — share notes via public link or with specific users
- **Google OAuth** — additional auth provider
- **Real-time sync** — WebSocket-based live sync across devices
- **Note version history** — view and restore previous versions
- **Tags** — additional organizational layer alongside folders
- **Collaborative editing** — multi-user editing on shared notes

---

## Development Notes

### Project Structure (Recommended)
```
notepad/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar/
│   │   │   ├── NoteList/
│   │   │   ├── NoteEditor/
│   │   │   └── Search/
│   │   ├── hooks/
│   │   ├── services/          # API client
│   │   ├── store/             # State management (Zustand or React Context)
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── notes.py
│   │   │   └── folders.py
│   │   ├── models/
│   │   ├── schemas/           # Pydantic models
│   │   ├── services/
│   │   ├── core/              # Config, security, database
│   │   └── main.py
│   ├── alembic/               # Database migrations
│   ├── requirements.txt
│   └── .env
├── docker-compose.yml         # PostgreSQL + app services
└── README.md
```

### Key Implementation Notes
- Use **Alembic** for database migrations
- Use **Pydantic** for request/response validation
- Use **asyncpg** as the async PostgreSQL driver with SQLAlchemy
- TipTap content should be stored as JSON for rich rendering, with a plain-text extraction for search indexing
- Debounce auto-save on the frontend (~1000ms after last keystroke)
- Use optimistic UI updates for starring, moving, and deleting notes
- Implement proper error boundaries and loading states in React
