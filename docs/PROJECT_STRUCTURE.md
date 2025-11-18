# ForgeAI Project Structure

## 📁 Directory Layout

```
forgeai/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry point
│   │   │
│   │   ├── api/               # API Routes
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py    # Authentication endpoints
│   │   │       ├── chat.py    # Chat & WebSocket endpoints
│   │   │       ├── files.py   # File upload/management
│   │   │       ├── workspaces.py
│   │   │       ├── flashcards.py
│   │   │       └── exams.py
│   │   │
│   │   ├── core/              # Core Configuration & Utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py      # Settings & environment variables
│   │   │   ├── database.py    # SQLAlchemy setup
│   │   │   ├── security.py    # JWT, password hashing
│   │   │   ├── brain.py       # AI functions (PDF, summarization)
│   │   │   └── kb.py          # Knowledge Base (RAG)
│   │   │
│   │   ├── models/            # Database Models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── workspace.py
│   │   │   ├── chat.py
│   │   │   ├── file.py
│   │   │   ├── flashcard.py
│   │   │   └── exam.py
│   │   │
│   │   └── services/          # Business Logic
│   │       ├── __init__.py
│   │       ├── ai_service.py  # Ollama AI integration
│   │       ├── file_service.py
│   │       └── rag_service.py
│   │
│   ├── alembic/               # Database Migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 001_initial.py
│   │
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                  # Next.js Frontend
│   ├── app/                   # App Router Pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Landing page
│   │   ├── providers.tsx      # React Query provider
│   │   ├── globals.css        # Global styles
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── (dashboard)/       # Protected routes
│   │       ├── layout.tsx
│   │       ├── chat/
│   │       │   └── page.tsx
│   │       ├── upload/
│   │       │   └── page.tsx
│   │       └── memory/
│   │           └── page.tsx
│   │
│   ├── components/            # React Components
│   │   ├── layout/
│   │   │   └── navbar.tsx
│   │   └── ui/                # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       └── input.tsx
│   │
│   ├── lib/                   # Utilities
│   │   ├── api.ts             # API client
│   │   └── utils.ts           # Helper functions
│   │
│   ├── middleware.ts          # Auth middleware
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── .env.example
│
├── docs/                      # Documentation
│   ├── SETUP.md
│   ├── QUICKSTART.md
│   ├── OLLAMA_SETUP.md
│   ├── DEPLOYMENT.md
│   └── PROJECT_STRUCTURE.md
│
├── kb_data/                   # Knowledge Base Storage (gitignored)
│   ├── texts.json
│   ├── vectors.npy
│   └── meta.json
│
├── README.md                  # Main documentation
├── .gitignore
└── venv/                      # Python virtual environment (gitignored)
```

## 🔑 Key Files

### Backend

- **`backend/app/main.py`** - FastAPI application entry point
- **`backend/app/core/config.py`** - Environment configuration
- **`backend/app/core/brain.py`** - AI functions (PDF processing, summarization)
- **`backend/app/core/kb.py`** - Knowledge Base (TF-IDF RAG)
- **`backend/app/services/ai_service.py`** - Ollama API integration
- **`backend/app/api/v1/chat.py`** - WebSocket chat endpoint

### Frontend

- **`frontend/app/layout.tsx`** - Root layout with providers
- **`frontend/app/(dashboard)/chat/page.tsx`** - Main chat interface
- **`frontend/lib/api.ts`** - API client for backend communication
- **`frontend/middleware.ts`** - Authentication middleware

## 📦 Dependencies

### Backend (`backend/requirements.txt`)
- FastAPI, Uvicorn
- SQLAlchemy, Alembic, PostgreSQL drivers
- Redis, Celery
- httpx (for Ollama)
- pypdf, python-pptx
- scikit-learn (TF-IDF)

### Frontend (`frontend/package.json`)
- Next.js 14
- React 18, TypeScript
- TailwindCSS, shadcn/ui
- Framer Motion
- React Query

## 🔄 Data Flow

1. **User** → Frontend (Next.js)
2. **Frontend** → API Client (`lib/api.ts`)
3. **API Client** → Backend (`app/api/v1/`)
4. **API Route** → Service Layer (`app/services/`)
5. **Service** → Core Functions (`app/core/`)
6. **Core** → External APIs (Ollama, Database, Redis)

## 🗄️ Database Schema

- **Users** - Authentication & profiles
- **Workspaces** - User workspaces
- **ChatSessions** - Chat conversations
- **ChatMessages** - Individual messages
- **Files** - Uploaded documents
- **Flashcards** - Study flashcards
- **Exams** - Exam sessions

## 🔐 Security

- JWT authentication
- Password hashing (bcrypt)
- CORS configuration
- Environment variables for secrets

## 🚀 Deployment

See [docs/DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

