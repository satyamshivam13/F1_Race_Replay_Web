# 🏎️ F1 Race Replay Web

**Interactive Formula 1 race replay and data visualization web application.**

Watch any F1 race from 1950 to present with animated car positions, live timing, and telemetry data.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                            │
│                    Next.js 14 + React + Pixi.js                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                    REST API + WebSocket
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Railway)                            │
│                    FastAPI + Python                             │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE                                     │
│    PostgreSQL (Neon) + Redis (Upstash) + FastF1 Cache          │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Backend (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run development server
uvicorn app.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### Frontend (Next.js)

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev
```

Open http://localhost:3000

## 📡 API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/seasons` | List all F1 seasons |
| GET | `/api/seasons/{year}` | Get season with events |
| GET | `/api/races/{year}/{round}` | Get event details |
| GET | `/api/races/{year}/{round}/{session}` | Get session with results |
| GET | `/api/races/{year}/{round}/{session}/laps` | Get lap data |
| GET | `/api/races/{year}/{round}/{session}/telemetry` | Get telemetry |

### WebSocket

Connect to `/ws/replay/{session_id}` for real-time replay streaming.

**Commands (client → server):**
```json
{ "action": "play" }
{ "action": "pause" }
{ "action": "seek", "time_ms": 60000 }
{ "action": "speed", "speed": 2.0 }
```

**Events (server → client):**
```json
{ "type": "frame", "data": { "cars": [...], "timestamp_ms": 1234 } }
{ "type": "status", "data": { "is_playing": true } }
{ "type": "finished" }
```

## 🔧 Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/f1replay

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key

# FastF1
FASTF1_CACHE_DIR=/tmp/fastf1
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🚢 Deployment

### Backend → Railway

1. Create a new project on [Railway](https://railway.app)
2. Add PostgreSQL database
3. Connect GitHub repo
4. Set environment variables
5. Deploy!

### Frontend → Vercel

1. Import project to [Vercel](https://vercel.com)
2. Set environment variables
3. Deploy!

### Docker (Local Development)

```bash
docker-compose up -d
```

## 📊 Data Coverage

| Era | Data Available |
|-----|----------------|
| 2018–Present | Full telemetry (GPS, speed, throttle, brake, gear, DRS) |
| 2011–2017 | Detailed lap data, sector times |
| 1996–2010 | Lap times, pit stops, results |
| 1950–1995 | Race results, grid positions |

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- SQLAlchemy 2.0 (async)
- PostgreSQL + asyncpg
- FastF1 for F1 data
- Redis for caching

**Frontend:**
- Next.js 14 (App Router)
- React 18 + TypeScript
- Pixi.js for visualization
- TailwindCSS + shadcn/ui
- Zustand for state

## 📄 License

MIT License
