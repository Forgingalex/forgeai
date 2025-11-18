# ForgeAI Setup Complete ✅

## What Has Been Done

### ✅ Environment Files Created
- `backend/.env` - Created from `.env.example`
- `frontend/.env.local` - Created from `.env.example`

### ✅ Code Improvements
- **WebSocket Authentication** - Token-based auth added to WebSocket connections
- **Error Handling** - Improved error messages and handling throughout frontend
- **Loading States** - Better loading indicators and user feedback
- **RAG Integration** - Memory page now properly connects to RAG endpoint

### ✅ Backend Structure
- All API endpoints implemented
- Database models ready
- Migrations configured
- Services integrated

### ✅ Frontend Structure
- All pages implemented
- Components ready
- API client configured
- WebSocket integration complete

## Next Steps - Manual Setup Required

### 1. Install Ollama ⚠️ REQUIRED

**Windows:**
1. Download from: https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically

**Verify installation:**
```powershell
ollama --version
```

**Pull the model:**
```powershell
ollama pull llama3.1:8b
```

**Verify model:**
```powershell
ollama list
```

**Test Ollama:**
```powershell
curl http://localhost:11434/api/tags
```

### 2. Install Backend Dependencies

```powershell
cd backend
python -m pip install -r requirements.txt
```

**Note:** If you're using a virtual environment:
```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```powershell
cd frontend
npm install
```

### 4. Set Up PostgreSQL Database ⚠️ REQUIRED

**Option A: Using createdb (if PostgreSQL is in PATH)**
```powershell
createdb forgeai
```

**Option B: Using psql**
```powershell
psql -U postgres
# Then in psql:
CREATE DATABASE forgeai;
\q
```

**Option C: Using pgAdmin**
1. Open pgAdmin
2. Right-click "Databases"
3. Create → Database
4. Name: `forgeai`
5. Save

### 5. Configure Database Connection

Edit `backend/.env` and update:
```env
DATABASE_URL=postgresql://username:password@localhost/forgeai
DATABASE_URL_ASYNC=postgresql+asyncpg://username:password@localhost/forgeai
```

**Default PostgreSQL credentials:**
- Username: `postgres`
- Password: (your PostgreSQL password)
- Host: `localhost`
- Port: `5432`

### 6. Run Database Migrations

```powershell
cd backend
alembic upgrade head
```

### 7. Start Backend Server

```powershell
cd backend
uvicorn app.main:app --reload
```

Backend will run on: `http://localhost:8000`
API docs: `http://localhost:8000/api/docs`

### 8. Start Frontend Server (New Terminal)

```powershell
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:3000`

### 9. Test the Application

1. **Visit:** http://localhost:3000
2. **Register** a new account
3. **Login** with your credentials
4. **Test Chat** - Send a message
5. **Upload a PDF** - Test file upload
6. **Test Memory** - Query your uploaded documents

## Troubleshooting

### Ollama Not Running
```powershell
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama service or restart it
```

### Database Connection Error
- Verify PostgreSQL is running
- Check credentials in `backend/.env`
- Ensure database `forgeai` exists

### Migration Errors
```powershell
# Reset migrations (WARNING: deletes all data)
cd backend
alembic downgrade base
alembic upgrade head
```

### Port Already in Use
- Backend: Change port in `uvicorn` command: `--port 8001`
- Frontend: Change port in `package.json` scripts or use: `npm run dev -- -p 3001`

### Module Not Found Errors
```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## Quick Checklist

- [ ] Ollama installed and running
- [ ] Model `llama3.1:8b` pulled
- [ ] PostgreSQL database `forgeai` created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Database migrations run (`alembic upgrade head`)
- [ ] Backend server running (`uvicorn app.main:app --reload`)
- [ ] Frontend server running (`npm run dev`)
- [ ] Tested registration/login
- [ ] Tested chat functionality
- [ ] Tested file upload

## Environment Variables Reference

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql://forgeai:forgeai@localhost/forgeai
DATABASE_URL_ASYNC=postgresql+asyncpg://forgeai:forgeai@localhost/forgeai
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Success Indicators

✅ **Backend Running:**
- Visit: http://localhost:8000/api/docs
- Should see Swagger UI

✅ **Frontend Running:**
- Visit: http://localhost:3000
- Should see login page

✅ **Ollama Working:**
```powershell
curl http://localhost:11434/api/tags
# Should return JSON with models
```

✅ **Database Connected:**
- Backend starts without database errors
- Migrations run successfully

---

**You're almost there!** Follow the steps above to complete the setup. 🚀

