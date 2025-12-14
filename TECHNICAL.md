# ForgeAI Technical Documentation

Complete technical reference for installation, configuration, and deployment.

## Features

- Streaming AI Chat - Real-time conversations with Ollama-powered AI
- PDF Summarization - Extract and summarize key information from documents
- RAG Memory System - Intelligent knowledge retrieval from your documents
- Study Planner - Generate personalized study schedules
- Exam Mode - AI-generated questions with automated grading
- Flashcard Generator - Create and manage study flashcards
- Voice Chat - Speak naturally with your AI assistant
- Workspace Management - Organize files, notes, and projects
- Cloud Memory - Persistent knowledge across sessions

## Tech Stack

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
- Ollama (Free, Local, Unlimited)
- Google AI Studio (Gemini API) - Optional primary provider
- LlamaIndex (RAG)
- TF-IDF (Knowledge Base)

## Project Structure

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

## Quick Start

### Prerequisites

- Python 3.9+ (Python 3.13 recommended)
- Node.js 18+
- PostgreSQL 12+
- Redis (optional, for caching and background tasks)
- Ollama - Download from https://ollama.ai/download

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

1. Backend: Visit http://localhost:8000/api/docs (Swagger UI)
2. Frontend: Visit http://localhost:3000
3. Ollama: Run `ollama list` to verify model is installed
4. Database: Backend should start without connection errors

## Troubleshooting

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

## API Configuration

### AI Models

The system supports dual-model architecture with automatic fallback:

**Primary**: Google AI Studio (Gemini)
- Model: `gemini-2.5-flash` (default)
- Requires: `GOOGLE_AI_API_KEY` in `.env`
- Fast, cloud-based, rate-limited

**Fallback**: Ollama (Local)
- Model: `llama3.1:8b` (default)
- Requires: Ollama running on `http://localhost:11434`
- Slower, unlimited, local-only

The system automatically falls back to Ollama when:
- Google AI rate limit is hit
- Daily quota is exceeded
- Network error occurs
- Google AI API key is not configured

### Environment Variables

**Backend** (`backend/.env`):
```env
# Database
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/forgeai
DATABASE_URL_ASYNC=postgresql+asyncpg://username:password@localhost:5432/forgeai

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Google AI (Optional)
GOOGLE_AI_API_KEY=your-api-key-here
GOOGLE_AI_MODEL=gemini-2.5-flash

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more testing guidelines.

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - System architecture and design decisions
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment guide
- [Contributing Guide](CONTRIBUTING.md) - How to contribute to ForgeAI
- [Code of Conduct](CODE_OF_CONDUCT.md) - Community guidelines

## Why Ollama?

- 100% Free - No API costs
- Unlimited Usage - No rate limits
- Privacy - Data stays local
- Offline - Works without internet
- Open Source - Fully transparent

## Architecture

- Modular Design - Clean separation of concerns
- Type-Safe - TypeScript + Pydantic
- Scalable - Async/await, background workers
- Production-Ready - Error handling, logging, migrations

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture documentation.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting PRs.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Roadmap

- Enhanced RAG with vector embeddings
- Mobile app support
- Collaborative workspaces
- Advanced analytics and insights
- Plugin system for extensibility
- Multi-language support

## Disclaimer

ForgeAI is provided as-is for educational and personal use. The AI models used (Ollama) are run locally and I'm not responsible for the content generated by these models.

