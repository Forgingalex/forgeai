# ForgeAI Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL
- Redis

## Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up database:**
```bash
# Create PostgreSQL database
createdb forgeai

# Run migrations
alembic upgrade head
```

5. **Start backend:**
```bash
uvicorn app.main:app --reload
```

Backend runs on `http://localhost:8000`

## Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Set up environment:**
```bash
cp .env.example .env.local
# Edit .env.local with API URL
```

3. **Start frontend:**
```bash
npm run dev
```

Frontend runs on `http://localhost:3000`

## Features

- ✅ Authentication (register/login)
- ✅ Chat with streaming responses
- ✅ File upload & processing
- ✅ PDF summarization
- ✅ RAG memory system
- ✅ Workspaces
- ✅ Flashcards
- ✅ Exam mode

## Next Steps

1. Set up Redis for caching and queues
2. Configure Celery for background tasks
3. Set up S3-compatible storage for production
4. Add more AI features (voice, image analysis, etc.)

