# Ollama Setup Guide for ForgeAI

## ✅ Changes Completed

All code has been updated to use **Ollama** instead of Groq:

1. ✅ `backend/app/core/config.py` - Updated with Ollama settings
2. ✅ `backend/app/services/ai_service.py` - Replaced Groq with Ollama API
3. ✅ `backend/app/core/brain.py` - Updated to use Ollama
4. ✅ `backend/app/core/kb.py` - Knowledge base functions
5. ✅ `backend/requirements.txt` - Removed groq dependency (httpx already included)
6. ✅ `backend/.env.example` - Created with Ollama settings
7. ✅ `frontend/.env.example` - Created with API URLs

## 🚀 Next Steps

### 1. Install Ollama

**Windows:**
1. Download from: https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically

**Verify installation:**
```bash
ollama --version
```

### 2. Pull a Model

```bash
# Pull Llama 3.1 8B (recommended)
ollama pull llama3.1:8b

# Or try other models:
# ollama pull llama3.1:70b      # Larger, better quality
# ollama pull mistral:7b         # Alternative
# ollama pull codellama:7b       # Code-focused
```

**Check available models:**
```bash
ollama list
```

### 3. Verify Ollama is Running

```bash
# Test API endpoint
curl http://localhost:11434/api/tags

# Or test in browser:
# http://localhost:11434/api/tags
```

### 4. Set Up Environment Files

**Backend:**
```bash
cd backend
copy .env.example .env
# Edit .env if needed (defaults should work)
```

**Frontend:**
```bash
cd frontend
copy .env.example .env.local
# Edit .env.local if needed (defaults should work)
```

### 5. Install Backend Dependencies

```bash
cd backend

# Activate virtual environment (if using root venv, skip this)
# .\venv\Scripts\activate  # Windows PowerShell

# Remove groq if installed
pip uninstall groq -y

# Install/update dependencies
pip install -r requirements.txt
```

### 6. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # First time only
npm run dev
```

### 7. Test Everything

1. **Check Ollama:** `curl http://localhost:11434/api/tags`
2. **Check Backend:** `http://localhost:8000/api/docs`
3. **Check Frontend:** `http://localhost:3000`
4. **Test Chat:** Register and send a message

## 🎯 Configuration

### Default Settings (in `.env`)

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
MODEL_NAME=llama3.1:8b
```

### Change Model

To use a different model:

1. Pull the model: `ollama pull <model-name>`
2. Update `.env`:
   ```env
   OLLAMA_MODEL=<model-name>
   MODEL_NAME=<model-name>
   ```
3. Restart backend server

## 🔧 Troubleshooting

### Ollama Not Running

**Windows:**
- Check if Ollama service is running
- Restart Ollama from Start Menu
- Or run: `ollama serve`

**Check status:**
```bash
curl http://localhost:11434/api/tags
```

### Model Not Found

```bash
# List available models
ollama list

# Pull the model if missing
ollama pull llama3.1:8b
```

### Backend Can't Connect to Ollama

1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check `OLLAMA_BASE_URL` in `backend/.env`
3. Ensure firewall allows localhost connections

### Slow Responses

- Use a smaller model: `llama3.1:8b` (faster)
- Or upgrade hardware (GPU recommended for larger models)
- Check system resources: Task Manager (Windows)

## 📊 Model Comparison

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| `llama3.1:8b` | ~4.7GB | Fast | Good | **Recommended** |
| `llama3.1:70b` | ~40GB | Slow | Excellent | High quality |
| `mistral:7b` | ~4.1GB | Fast | Good | Alternative |
| `codellama:7b` | ~3.8GB | Fast | Good | Code-focused |

## ✨ Benefits of Ollama

- ✅ **100% Free** - No API costs
- ✅ **Unlimited Usage** - No rate limits
- ✅ **Privacy** - Data stays local
- ✅ **Offline** - Works without internet
- ✅ **Open Source** - Fully transparent
- ✅ **Customizable** - Use any model

## 🎉 You're All Set!

Your ForgeAI app now uses Ollama for completely free, unlimited AI responses!

