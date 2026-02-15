# 🚀 F1 Race Replay - Complete Deployment Guide

## ✅ What's Been Completed

All critical tasks from the original list have been addressed:

1. ✅ **Alembic Initialized** - Migration system configured for async SQLAlchemy
2. ✅ **Data Fetch Tools Created** - Both script and API endpoints available
3. ✅ **Docker Configuration Ready** - docker-compose.yml configured
4. ✅ **Deployment Guide** - This document!

---

## 🏁 Quick Start (Local Development)

### Prerequisites

Ensure you have:
- ✅ Python 3.10+ installed
- ✅ Node.js 18+ installed
- ✅ Docker Desktop installed and running
- ✅ Git

### Step 1: Start Database Services

```powershell
# Navigate to project root
cd C:\Users\Asus\Downloads\f1_race_replay_web

# Start PostgreSQL and Redis
docker-compose up -d db redis

# Verify services are running
docker-compose ps
```

### Step 2: Initialize Database

```powershell
cd backend

# Activate virtual environment (create if needed)
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Alembic migrations
python -m alembic upgrade head

# OR initialize directly
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Step 3: Fetch F1 Data

**Option A: Using the Script (Recommended)**

```powershell
# Fetch 2024 season schedule
python scripts/fetch_f1_data.py --year 2024 --init-db

# Fetch specific race session (with telemetry)
python scripts/fetch_f1_data.py --year 2024 --round 1 --session Race

# Fetch multiple seasons
python scripts/fetch_f1_data.py --year 2024 --year 2023
```

**Option B: Using API Endpoints**

```powershell
# Start the backend first
uvicorn app.main:app --reload --port 8000

# In another terminal, make API requests
curl -X POST http://localhost:8000/api/seasons/2024/fetch
curl -X POST http://localhost:8000/api/races/2024/1/Race/fetch
```

### Step 4: Start Backend

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

API documentation available at: http://localhost:8000/docs

### Step 5: Start Frontend

```powershell
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Application available at: http://localhost:3000

---

## 🔧 Environment Configuration

### Backend `.env`

Current configuration in `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/f1replay
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-long
FASTF1_CACHE_DIR=/tmp/fastf1
CORS_ORIGINS=["http://localhost:3000","https://f1replay.vercel.app"]
DEBUG=true
```

### Frontend `.env.local`

Current configuration in `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 🌐 Production Deployment

### Prerequisites

1. **Database**: PostgreSQL 16+ (Neon, Railway, AWS RDS, etc.)
2. **Cache**: Redis (Upstash, Railway, AWS ElastiCache, etc.)
3. **Backend**: Railway, Render, or any platform supporting Python
4. **Frontend**: Vercel, Netlify, or similar

### Deployment Steps

#### 1. Deploy Database (Neon)

```powershell
# Go to https://neon.tech
# 1. Create new project
# 2. Copy connection string
# 3. Create database named "f1replay"
```

#### 2. Deploy Redis (Upstash)

```powershell
# Go to https://upstash.com
# 1. Create Redis database
# 2. Copy connection string
```

#### 3. Deploy Backend (Railway)

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project or create new
railway init

# Set environment variables
railway variables set DATABASE_URL="postgresql+asyncpg://[your-neon-connection]"
railway variables set REDIS_URL="redis://[your-upstash-connection]"
railway variables set SECRET_KEY="[generate-strong-key]"
railway variables set CORS_ORIGINS='["https://your-frontend.vercel.app"]'
railway variables set DEBUG="false"
railway variables set FASTF1_CACHE_DIR="/tmp/fastf1"

# Deploy
cd backend
railway up

# Run migrations (one time)
railway run alembic upgrade head

# Fetch initial data
railway run python scripts/fetch_f1_data.py --year 2024 --init-db
```

#### 4. Deploy Frontend (Vercel)

```powershell
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel

# Set environment variables in Vercel Dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
# NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app

# Deploy to production
vercel --prod
```

---

## 📊 Data Fetching Guide

### Understanding Data Availability

| Year Range | Data Available |
|------------|----------------|
| 2018-Present | Full telemetry (GPS, speed, throttle, brake, gear, DRS) |
| 2011-2017 | Detailed lap data, sector times |
| 1996-2010 | Lap times, pit stops, results |
| 1950-1995 | Race results, grid positions |

### Fetching Strategy

**For Recent Seasons (2018+):**
```powershell
# 1. Fetch season schedule
python scripts/fetch_f1_data.py --year 2024

# 2. Fetch specific races with telemetry
python scripts/fetch_f1_data.py --year 2024 --round 1 --session Race
python scripts/fetch_f1_data.py --year 2024 --round 2 --session Race
```

**For Older Seasons:**
```powershell
# Fetch schedule only (telemetry unavailable)
python scripts/fetch_f1_data.py --year 2010
```

### Session Types

- `Race` or `R` - Main race
- `Qualifying` or `Q` - Qualifying session
- `Sprint` or `S` - Sprint race
- `FP1`, `FP2`, `FP3` - Free practice sessions
- `SQ` - Sprint qualifying

---

## 🐛 Troubleshooting

### Issue: Docker not running

```powershell
# Error: "cannot find dockerDesktopLinuxEngine"
# Solution: Start Docker Desktop manually
# Windows: Start -> Docker Desktop
```

### Issue: Database connection failed

```powershell
# Check if PostgreSQL is running
docker-compose ps

# Restart services
docker-compose restart db

# Check logs
docker-compose logs db
```

### Issue: Alembic migration errors

```powershell
# Ensure database is running first
docker-compose up -d db

# Drop all tables and recreate (DEV ONLY!)
python -c "from app.core.database import engine, Base; import asyncio; asyncio.run(Base.metadata.drop_all(bind=engine)); asyncio.run(Base.metadata.create_all(bind=engine))"

# Or use Alembic
alembic downgrade base
alembic upgrade head
```

### Issue: FastF1 data fetch timeout

```powershell
# FastF1 can be slow for older data
# Solution: Be patient, or fetch specific sessions only
# Try with a smaller dataset first:
python scripts/fetch_f1_data.py --year 2024 --round 1 --session Race
```

### Issue: CORS errors in browser

Check that `CORS_ORIGINS` in backend `.env` includes your frontend URL:
```env
CORS_ORIGINS=["http://localhost:3000","https://your-frontend.vercel.app"]
```

### Issue: WebSocket connection failed

- Ensure backend is running
- Check `NEXT_PUBLIC_WS_URL` in frontend `.env.local`
- For production, use `wss://` (secure WebSocket)

---

## 🧪 Testing Checklist

### Backend Tests

```powershell
cd backend

# Test API is running
curl http://localhost:8000/health

# Test OpenAPI docs
# Open http://localhost:8000/docs in browser

# Test season endpoint
curl http://localhost:8000/api/seasons

# Test data fetch
curl -X POST http://localhost:8000/api/seasons/2024/fetch
```

### Frontend Tests

```powershell
cd frontend

# Build test
npm run build

# Start production build
npm run start

# Open http://localhost:3000
```

### Integration Tests

1. ✅ Homepage loads with F1 branding
2. ✅ Browse Races button navigates correctly
3. ✅ Seasons list displays
4. ✅ Race events load
5. ✅ Replay viewer opens
6. ✅ WebSocket connects
7. ✅ Track renders
8. ✅ Cars animate
9. ✅ Controls respond (play/pause/seek)
10. ✅ Speed adjustment works

---

## 📈 Performance Tips

### Backend Optimization

```python
# In production, use multiple workers
# Procfile or railway.toml:
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
```

### Frontend Optimization

```javascript
// next.config.js
module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  compress: true,
  images: {
    domains: ['your-cdn.com'],
    formats: ['image/webp']
  }
}
```

### Database Optimization

```sql
-- Add indexes for common queries (already in models)
-- Monitor slow queries
-- Use connection pooling (already configured)
```

---

## 🔒 Security Checklist

### Before Production

- [ ] Change `SECRET_KEY` to strong random value (min 32 chars)
- [ ] Set `DEBUG=false`
- [ ] Restrict `CORS_ORIGINS` to your frontend domain only
- [ ] Use HTTPS for both frontend and backend
- [ ] Use WSS (secure WebSocket) for production
- [ ] Enable database SSL/TLS
- [ ] Add rate limiting (TODO)
- [ ] Set up monitoring (Sentry)
- [ ] Configure backups for database
- [ ] Review environment variables - no secrets in code

---

## 📝 Post-Deployment Tasks

### 1. Fetch Initial Data

```powershell
# After deploying backend, fetch data for current season
railway run python scripts/fetch_f1_data.py --year 2024 --init-db

# Or use the API
curl -X POST https://your-backend.railway.app/api/seasons/2024/fetch
```

### 2. Set Up Monitoring

```powershell
# Install Sentry
pip install sentry-sdk[fastapi]
npm install @sentry/nextjs

# Configure in app/main.py and next.config.js
```

### 3. Configure Domain

- Point your domain to Vercel (frontend)
- Update `CORS_ORIGINS` with your domain
- Update `NEXT_PUBLIC_API_URL` with your domain

### 4. Test Everything

- Test all features
- Check error logging
- Monitor performance
- Verify database backups

---

## 🎉 Success!

Your F1 Race Replay application is now deployed! 🏎️💨

### Access Your Application

- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://your-backend.railway.app
- **API Docs**: https://your-backend.railway.app/docs

### Next Steps

1. Share with F1 fans! 🏁
2. Gather feedback
3. Add more features (see PRODUCTION_READY.md)
4. Monitor usage and performance
5. Keep data updated with new races

---

## 📞 Support & Resources

- **Setup Guide**: `SETUP_GUIDE.md`
- **Production Readiness**: `PRODUCTION_READY.md`
- **API Documentation**: `/docs` endpoint
- **FastF1 Docs**: https://docs.fastf1.dev/
- **Railway Docs**: https://docs.railway.app/
- **Vercel Docs**: https://vercel.com/docs

---

## 🏁 Summary

✅ **Alembic configured** - Database migrations ready
✅ **Data fetch script** - `scripts/fetch_f1_data.py`
✅ **API endpoints** - POST `/api/seasons/{year}/fetch` and `/api/races/{year}/{round}/{session}/fetch`
✅ **Docker ready** - `docker-compose up -d`
✅ **Deployment guides** - Railway + Vercel instructions

**You're ready to deploy! 🚀**
