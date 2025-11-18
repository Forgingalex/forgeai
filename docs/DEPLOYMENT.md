# ForgeAI Deployment Guide

## Production Deployment Checklist

### 1. Environment Variables

#### Backend (`backend/.env`)

```env
# Database - Use production PostgreSQL
DATABASE_URL=postgresql+psycopg://user:password@host:5432/forgeai
DATABASE_URL_ASYNC=postgresql+asyncpg://user:password@host:5432/forgeai

# Security - Generate a strong secret key
SECRET_KEY=<generate-random-64-character-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Ollama - Update if using remote instance
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# CORS - Add your production domain
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Redis (if using)
REDIS_URL=redis://your-redis-host:6379/0
```

#### Frontend (`frontend/.env.production`)

```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

### 2. Security Hardening

#### Backend Security

1. **Generate Strong Secret Key**:
   ```python
   import secrets
   print(secrets.token_urlsafe(64))
   ```

2. **Enable HTTPS**: Use reverse proxy (Nginx/Caddy) with SSL certificates

3. **Rate Limiting**: Add rate limiting middleware:
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

4. **CORS Configuration**: Restrict to production domains only

5. **Input Validation**: All endpoints already use Pydantic validation

6. **SQL Injection Protection**: Using SQLAlchemy ORM (already protected)

#### Frontend Security

1. **Environment Variables**: Never commit `.env.local` or `.env.production`
2. **HTTPS Only**: Configure Next.js to enforce HTTPS
3. **Content Security Policy**: Add CSP headers
4. **XSS Protection**: React automatically escapes, but add additional headers

### 3. Database Setup

#### Production PostgreSQL

1. **Create Production Database**:
   ```sql
   CREATE DATABASE forgeai_production;
   CREATE USER forgeai_user WITH PASSWORD 'strong_password';
   GRANT ALL PRIVILEGES ON DATABASE forgeai_production TO forgeai_user;
   ```

2. **Run Migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Backup Strategy**: Set up automated backups
   ```bash
   # Daily backup script
   pg_dump -U forgeai_user forgeai_production > backup_$(date +%Y%m%d).sql
   ```

4. **Connection Pooling**: Configure SQLAlchemy pool settings:
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=20,
       max_overflow=40,
       pool_pre_ping=True
   )
   ```

### 4. Server Configuration

#### Backend (FastAPI)

**Option 1: Using Uvicorn with Gunicorn** (Recommended)
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

**Option 2: Using Docker**
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 3: Systemd Service** (Linux)
```ini
[Unit]
Description=ForgeAI Backend
After=network.target

[Service]
User=forgeai
WorkingDirectory=/opt/forgeai/backend
Environment="PATH=/opt/forgeai/backend/venv/bin"
ExecStart=/opt/forgeai/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Frontend (Next.js)

**Build for Production**:
```bash
cd frontend
npm run build
npm start
```

**Using PM2**:
```bash
npm install -g pm2
pm2 start npm --name "forgeai-frontend" -- start
pm2 save
pm2 startup
```

**Docker**:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### 5. Reverse Proxy (Nginx)

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 6. SSL/TLS Setup

**Using Let's Encrypt (Certbot)**:
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

### 7. Monitoring & Logging

#### Application Monitoring

1. **Health Check Endpoint**: Already available at `/health`
2. **Error Tracking**: Integrate Sentry:
   ```python
   import sentry_sdk
   sentry_sdk.init(dsn="your-sentry-dsn")
   ```

3. **Logging**: Configure structured logging:
   ```python
   import logging
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

#### System Monitoring

- **Uptime Monitoring**: Use UptimeRobot, Pingdom, or similar
- **Server Monitoring**: Use Datadog, New Relic, or Prometheus + Grafana
- **Database Monitoring**: PostgreSQL monitoring tools

### 8. Performance Optimization

1. **Redis Caching**: Enable Redis for session storage and caching
2. **CDN**: Use Cloudflare or AWS CloudFront for static assets
3. **Database Indexing**: Ensure proper indexes on frequently queried columns
4. **Connection Pooling**: Configure database connection pools
5. **Static File Serving**: Serve static files through Nginx/CDN

### 9. Backup Strategy

1. **Database Backups**: Daily automated backups
2. **File Storage**: Backup uploaded files to S3 or similar
3. **Configuration**: Version control all config files
4. **Disaster Recovery**: Document recovery procedures

### 10. Scaling Considerations

#### Horizontal Scaling

- **Load Balancer**: Use Nginx or cloud load balancer
- **Multiple Backend Instances**: Run multiple FastAPI instances
- **Database Replication**: Set up PostgreSQL read replicas
- **Session Storage**: Use Redis for shared session storage

#### Vertical Scaling

- **Increase Server Resources**: More CPU/RAM for Ollama
- **Database Optimization**: Tune PostgreSQL settings
- **Caching**: Aggressive caching strategy

### 11. Deployment Platforms

#### Option 1: VPS (DigitalOcean, Linode, etc.)

- Full control
- Requires server management
- Cost-effective for small-medium scale

#### Option 2: Cloud Platforms

**AWS**:
- EC2 for backend
- RDS for PostgreSQL
- S3 for file storage
- CloudFront for CDN

**Google Cloud**:
- Cloud Run for backend (serverless)
- Cloud SQL for PostgreSQL
- Cloud Storage for files

**Azure**:
- App Service for backend
- Azure Database for PostgreSQL
- Blob Storage for files

#### Option 3: Container Platforms

**Docker Compose**:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=forgeai
      - POSTGRES_USER=forgeai
      - POSTGRES_PASSWORD=password
```

**Kubernetes**: For large-scale deployments

### 12. Post-Deployment Checklist

- [ ] SSL certificates installed and working
- [ ] Database migrations run successfully
- [ ] Environment variables configured
- [ ] Backend API accessible and responding
- [ ] Frontend loading correctly
- [ ] WebSocket connections working
- [ ] File uploads working
- [ ] Ollama responding to requests
- [ ] Monitoring and alerts configured
- [ ] Backups scheduled and tested
- [ ] Documentation updated with production URLs

## Support

For deployment issues, check:
- [Setup Guide](SETUP.md)
- [Troubleshooting](SETUP.md#troubleshooting)
- GitHub Issues: https://github.com/Forgingalex/ForgeAI/issues
