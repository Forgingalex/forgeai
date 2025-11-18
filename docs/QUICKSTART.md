# ForgeAI Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API keys:
# - GROQ_API_KEY (from your config.py)
# - OPENAI_API_KEY (optional)
# - Set DATABASE_URL (PostgreSQL)
# - Set REDIS_URL

# Initialize database (PostgreSQL must be running)
createdb forgeai  # or use pgAdmin
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Start frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

### 3. Access the App

1. Open `http://localhost:3000`
2. Register a new account
3. Start chatting!

## 📋 Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL installed and running
- [ ] Redis installed and running (optional for now)
- [ ] Groq API key (from your config.py)

## 🔧 Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Check Redis is running: `redis-cli ping`
- Verify .env file has correct values

### Frontend won't connect
- Check backend is running on port 8000
- Verify NEXT_PUBLIC_API_URL in .env.local
- Check browser console for CORS errors

### Database errors
- Run migrations: `alembic upgrade head`
- Check DATABASE_URL in .env
- Ensure database exists: `createdb forgeai`

## 🎯 Next Steps

1. **Test Chat**: Send a message and see streaming responses
2. **Upload Files**: Upload a PDF and get summaries
3. **Use RAG**: Upload files, then ask questions about them
4. **Explore Features**: Check out workspaces, flashcards, exams

## 📚 Documentation

- See `PROJECT_STRUCTURE.md` for architecture details
- See `SETUP.md` for detailed setup instructions
- API docs available at `http://localhost:8000/api/docs`

