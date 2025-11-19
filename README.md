# ForgeAI

> **Think Faster. Learn Smarter.**

A premium AI-powered study companion designed to forge understanding, accelerate learning, and simplify complex ideas.

## ✨ Features

- 💬 **Streaming AI Chat** - Real-time conversations with Ollama-powered AI
- 📄 **PDF Summarization** - Extract and summarize key information from documents
- 🧠 **RAG Memory System** - Intelligent knowledge retrieval from your documents
- 📝 **Study Planner** - Generate personalized study schedules
- 🎓 **Exam Mode** - AI-generated questions with automated grading
- 🃏 **Flashcard Generator** - Create and manage study flashcards
- 🎤 **Voice Chat** - Speak naturally with your AI assistant
- 📊 **Workspace Management** - Organize files, notes, and projects
- ☁️ **Cloud Memory** - Persistent knowledge across sessions

## 🚀 Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- React 18 + TypeScript
- TailwindCSS + shadcn/ui
- Framer Motion
- React Query

**Backend:**
- FastAPI (Python)
- PostgreSQL + SQLAlchemy
- Redis (caching & queues)
- WebSockets (real-time streaming)
- Celery (background tasks)

**AI:**
- **Ollama** (Free, Local, Unlimited)
- LlamaIndex (RAG)
- TF-IDF (Knowledge Base)

## 📁 Project Structure

```
forgeai/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/      # API routes
│   │   ├── core/        # Config, brain, kb, security
│   │   ├── models/      # Database models
│   │   └── services/    # Business logic
│   ├── alembic/         # Database migrations
│   └── requirements.txt
├── frontend/            # Next.js frontend
│   ├── app/             # App router pages
│   ├── components/      # React components
│   └── lib/             # Utilities
├── docs/                # Documentation
└── README.md
```

## 🛠️ Quick Start

### Prerequisites

- Python 3.9+ (Python 3.13 recommended)
- Node.js 18+
- PostgreSQL 12+
- Redis (optional, for caching and background tasks)
- **Ollama** - Download from https://ollama.ai/download

### 1. Install Ollama

```bash
# Download from https://ollama.ai/download
# Then pull a model:
ollama pull llama3.1:8b
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install pydantic-core --only-binary :all:  # Fix for Python 3.13
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials:
# DATABASE_URL=postgresql+psycopg://username:password@localhost/forgeai
# DATABASE_URL_ASYNC=postgresql+asyncpg://username:password@localhost/forgeai

# Create PostgreSQL database
# Option 1: Using createdb command
createdb forgeai

# Option 2: Using psql
psql -U postgres
CREATE DATABASE forgeai;
\q

# Option 3: Using pgAdmin GUI
# Right-click "Databases" → Create → Database → Name: forgeai

# Run database migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
# Edit .env.local if needed (defaults work for local development)

# Start dev server
npm run dev
```

### 4. Verify Installation

1. **Backend**: Visit http://localhost:8000/api/docs (Swagger UI)
2. **Frontend**: Visit http://localhost:3000
3. **Ollama**: Run `ollama list` to verify model is installed
4. **Database**: Backend should start without connection errors

## 🐛 Troubleshooting

### Backend Dependencies Issues

**Problem**: `pydantic-core` requires Rust/Cargo
**Solution**: 
```bash
pip install pydantic-core --only-binary :all:
pip install -r requirements.txt
```

**Problem**: `asyncpg` or `hiredis` build errors
**Solution**: These are optional. Comment them out in `requirements.txt` if you don't need async PostgreSQL or Redis performance optimizations.

**Problem**: `numpy` build errors on Python 3.13
**Solution**: Python 3.13 requires numpy 2.x. Update `langchain` to >=0.1.0 for compatibility.

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready` or check Windows Services
- Check credentials in `backend/.env`
- Ensure database `forgeai` exists
- Test connection: `psql -U username -d forgeai`

### Ollama Issues

- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Pull model: `ollama pull llama3.1:8b`
- Check model: `ollama list`

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment guide

## 🎯 Why Ollama?

- ✅ **100% Free** - No API costs
- ✅ **Unlimited Usage** - No rate limits
- ✅ **Privacy** - Data stays local
- ✅ **Offline** - Works without internet
- ✅ **Open Source** - Fully transparent

## 🏗️ Architecture

- **Modular Design** - Clean separation of concerns
- **Type-Safe** - TypeScript + Pydantic
- **Scalable** - Async/await, background workers
- **Production-Ready** - Error handling, logging, migrations

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

---

**Built with ❤️ for students and learners worldwide.**
