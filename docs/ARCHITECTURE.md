# ForgeAI Architecture Documentation

## Overview

ForgeAI is a full-stack AI-powered study platform built with FastAPI (backend) and Next.js (frontend). This document describes the system architecture, design decisions, and key components.

## System Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │◄───────►│    Backend      │
│   (Next.js)    │  HTTP   │   (FastAPI)     │
└─────────────────┘         └─────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │   PostgreSQL    │
                            │   (Database)    │
                            └─────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │     Ollama      │
                            │   (AI Engine)   │
                            └─────────────────┘
```

## Backend Architecture

### API Layer (`app/api/v1/`)

- **auth.py**: Authentication and authorization
- **chat.py**: Real-time chat with WebSocket support
- **files.py**: File upload and processing
- **flashcards.py**: Flashcard management
- **exams.py**: Exam generation and grading
- **study_planner.py**: Study plan creation
- **rag.py**: RAG query endpoints
- **workspaces.py**: Workspace management

### Core Layer (`app/core/`)

- **brain.py**: AI processing functions
- **kb.py**: Knowledge base (RAG) implementation
- **database.py**: Database connection and session management
- **security.py**: Authentication and password hashing
- **config.py**: Application configuration
- **logging_config.py**: Structured logging setup
- **exceptions.py**: Custom exception classes
- **rate_limit.py**: Rate limiting utilities
- **cache.py**: Caching utilities

### Services Layer (`app/services/`)

- **ai_service.py**: AI service abstraction
- **file_service.py**: File processing logic
- **rag_service.py**: RAG service wrapper

### Models Layer (`app/models/`)

SQLAlchemy ORM models for database tables:
- User, ChatSession, ChatMessage
- File, Workspace
- FlashcardSet, Flashcard
- ExamSession, ExamQuestion
- StudyPlan, StudySession

## Key Design Decisions

### Why TF-IDF over Embeddings for RAG?

**Decision**: Use TF-IDF vectorization instead of embeddings (e.g., OpenAI embeddings, Cohere)

**Rationale**:
1. **Simplicity**: No external vector database needed (e.g., Pinecone, Weaviate)
2. **Cost**: Free, no API costs
3. **Performance**: Good enough for small-medium knowledge bases (<10k documents)
4. **Privacy**: All processing stays local
5. **Maintainability**: Easier to debug and understand
6. **Upgrade Path**: Can be upgraded to embeddings later if needed

**Trade-offs**:
- Less semantic understanding than embeddings
- May not capture synonyms as well
- Performance degrades with very large knowledge bases

**Future Consideration**: If knowledge base grows beyond 10k documents, consider migrating to embeddings with a vector database.

### Why Ollama for AI?

**Decision**: Use Ollama (local LLM) instead of OpenAI/Anthropic APIs

**Rationale**:
1. **Cost**: Free, unlimited usage
2. **Privacy**: Data stays local
3. **No Rate Limits**: No API rate limiting concerns
4. **Offline**: Works without internet
5. **Open Source**: Fully transparent

**Trade-offs**:
- Requires local installation
- May be slower than cloud APIs
- Model quality depends on local hardware

### Why FastAPI?

**Decision**: Use FastAPI instead of Flask or Django

**Rationale**:
1. **Performance**: Fast, async support
2. **Type Safety**: Built-in Pydantic validation
3. **Documentation**: Auto-generated OpenAPI docs
4. **Modern**: Python 3.7+ features
5. **WebSocket**: Built-in WebSocket support

### Why Next.js?

**Decision**: Use Next.js instead of Create React App or Vite

**Rationale**:
1. **App Router**: Modern routing system
2. **Server Components**: Better performance
3. **TypeScript**: Built-in TypeScript support
4. **Deployment**: Easy deployment on Vercel
5. **SEO**: Better SEO capabilities

## Database Schema

### Key Relationships

- **User** → **ChatSession** (one-to-many)
- **User** → **File** (one-to-many)
- **User** → **FlashcardSet** (one-to-many)
- **User** → **ExamSession** (one-to-many)
- **User** → **StudyPlan** (one-to-many)
- **ChatSession** → **ChatMessage** (one-to-many)
- **FlashcardSet** → **Flashcard** (one-to-many)
- **ExamSession** → **ExamQuestion** (one-to-many)
- **StudyPlan** → **StudySession** (one-to-many)

## Security

### Authentication

- JWT tokens for stateless authentication
- Password hashing with bcrypt
- Token expiration (7 days default)

### Authorization

- User-based access control
- All endpoints verify user ownership
- WebSocket authentication via token

### Input Validation

- Pydantic models for request validation
- SQL injection protection via SQLAlchemy ORM
- File size limits (50MB max)

### Rate Limiting

- In-memory rate limiting (upgrade to Redis in production)
- 10 uploads per minute
- Configurable per endpoint

## Performance Optimizations

### Caching

- In-memory caching for RAG queries (5-minute TTL)
- Can be upgraded to Redis for distributed caching

### Database Optimization

- Indexed foreign keys
- Efficient queries with proper filtering
- Connection pooling

### File Processing

- Page-by-page PDF processing to avoid memory issues
- Text chunking with size limits
- Async processing in thread pool

## Error Handling

### Custom Exceptions

- `ForgeAIException`: Base exception
- `ValidationError`: Input validation failures
- `AuthenticationError`: Auth failures
- `NotFoundError`: Resource not found
- `ProcessingError`: File processing failures
- `AIServiceError`: AI service failures

### Logging

- Structured logging with rotation
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- File and console handlers

## Monitoring

### Current Implementation

- Structured logging
- Error tracking ready (Sentry integration ready)
- Health check endpoints

### Production Recommendations

- Add Sentry for error tracking
- Add Prometheus metrics
- Add APM (Application Performance Monitoring)
- Add uptime monitoring

## Deployment

### Backend

- Deploy to Railway, Render, or Fly.io
- Use managed PostgreSQL
- Set environment variables
- Run migrations on startup

### Frontend

- Deploy to Vercel (recommended)
- Set environment variables
- Configure API URL

### Database

- Use managed PostgreSQL (e.g., Railway, Supabase)
- Run migrations: `alembic upgrade head`
- Backup regularly

## Future Improvements

1. **Redis Integration**: Replace in-memory cache/rate limiting
2. **Vector Database**: Migrate RAG to embeddings if knowledge base grows
3. **Background Jobs**: Use Celery for long-running tasks
4. **Monitoring**: Add Sentry, Prometheus, APM
5. **Testing**: Increase test coverage
6. **Documentation**: Add more API documentation
7. **Performance**: Add database query optimization
8. **Security**: Add rate limiting per user, not just IP

## Development Guidelines

### Code Style

- Use Black for Python formatting
- Use Prettier for TypeScript formatting
- Follow PEP 8 for Python
- Use type hints everywhere

### Testing

- Unit tests for core functions
- Integration tests for API endpoints
- Aim for >80% code coverage

### Documentation

- Docstrings for all functions
- Type hints for all parameters
- Architecture documentation (this file)
- API documentation (Swagger)

