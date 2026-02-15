# 🏎️ F1 Race Replay Web

Interactive Formula 1 race replay and data visualization web application. Watch any F1 race from 1950 to present with animated car positions, live timing, and telemetry data.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)](https://www.python.org/)

## ✨ Features

- 🎬 **Interactive Race Replays** - Watch races play out with animated car positions
- 📊 **Rich Telemetry Data** - Speed, throttle, brake, gear, and DRS information
- 🏁 **Live Timing** - Lap times, pit stops, and position changes
- 📈 **Data Visualization** - Track position, standings, and performance analytics
- 🔞 **Historical Data** - Coverage from 1950 to current season (data availability varies)
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile devices
- ⚡ **Real-time WebSocket** - Live race replay streaming and control
- 🎯 **Advanced Filtering** - Filter by driver, team, lap number, and more

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

## � Prerequisites

- **Node.js** 18.x or higher (for frontend)
- **Python** 3.10 or higher (for backend)
- **PostgreSQL** 14+ (for database)
- **Redis** (optional, for caching)
- **Git** for version control
- **Docker** & **Docker Compose** (optional, for containerized setup)

## 🚀 Quick Start

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/f1_race_replay_web.git
cd f1_race_replay_web
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations (if using Alembic)
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

Backend API will be available at: **http://localhost:8000**
Interactive API docs: **http://localhost:8000/docs**

### Frontend Setup

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

Frontend will be available at: **http://localhost:3000**

### Using Docker Compose (All-in-One)

```bash
# From project root
docker-compose up -d

# Backend will be at http://localhost:8000
# Frontend will be at http://localhost:3000
```

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
- FastAPI (Python web framework)
- SQLAlchemy 2.0 (async ORM)
- PostgreSQL + asyncpg (async database driver)
- FastF1 (F1 data library)
- Redis (caching)
- Alembic (database migrations)

**Frontend:**
- Next.js 14 (React framework with App Router)
- React 18 + TypeScript
- Pixi.js (WebGL 2D renderer for track visualization)
- TailwindCSS + shadcn/ui (styling)
- Zustand (state management)
- WebSocket (real-time communication)

**DevOps & Deployment:**
- Docker & Docker Compose (containerization)
- Railway (backend hosting)
- Vercel (frontend hosting)
- PostgreSQL (database)
- Redis (cache)

## 📁 Project Structure

```
f1_race_replay_web/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── api/               # API routes and WebSocket
│   │   ├── core/              # Config, database, middleware
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── alembic/               # Database migrations
│   ├── scripts/               # Utility scripts
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Example environment variables
│   └── Dockerfile             # Container definition
│
├── frontend/                   # Next.js frontend
│   ├── app/                   # App Router pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── races/             # Race pages
│   ├── components/            # React components
│   │   ├── controls/          # Replay controls
│   │   ├── panels/            # Data panels
│   │   └── track/             # Track visualization
│   ├── lib/                   # Utilities and hooks
│   ├── public/                # Static files
│   ├── package.json           # Node dependencies
│   ├── .env.example           # Example environment variables
│   └── tailwind.config.js     # Tailwind configuration
│
├── .gitignore                 # Git ignore rules
├── docker-compose.yml         # Multi-container setup
├── README.md                  # This file
└── SETUP_GUIDE.md            # Detailed setup instructions
```

## 🔧 Environment Variables

### Backend (.env)

See [backend/.env.example](backend/.env.example) for complete list:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/f1replay
SQLALCHEMY_DATABASE_URL=postgresql://user:password@localhost:5432/f1replay

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# FastF1
FASTF1_CACHE_DIR=/tmp/fastf1_cache
```

### Frontend (.env.local)

See [frontend/.env.example](frontend/.env.example) for complete list:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_APP_NAME=F1 Race Replay
```

## 🏗️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting and formatting
cd backend
black app/
flake8 app/
mypy app/

# Frontend linting and formatting
cd frontend
npm run lint
npm run format
```

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Description of change"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🚢 Deployment

### Deployment Platforms

**Frontend (Vercel):**
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Vercel automatically deploys on push to main

**Backend (Railway):**
1. Create project on [Railway.app](https://railway.app)
2. Add PostgreSQL plugin
3. Connect GitHub repository
4. Set environment variables
5. Railway automatically deploys on push to main

**Frontend (Alternative - Netlify):**
```bash
npm run build
# Deploy build/ folder to Netlify
```

### Self-Hosted Deployment

```bash
# Build images
docker build -t f1-backend -f backend/Dockerfile ./backend
docker build -t f1-frontend -f frontend/Dockerfile ./frontend

# Run with Docker Compose
docker-compose up -d
```

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

**Database connection error:**
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists and credentials are correct

**Module not found errors:**
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Issues

**Port 3000 already in use:**
```bash
npm run dev -- -p 3001
```

**Module not found errors:**
```bash
cd frontend
npm install
npm run dev
```

**API connection issues:**
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Ensure backend is running on correct port
- Check browser console for CORS errors

## 📊 Data Coverage

| Era | Data Available | Coverage |
|-----|----------------|----------|
| 2018–Present | Full telemetry (GPS, speed, throttle, brake, gear, DRS) | 100% |
| 2011–2017 | Detailed lap data, sector times | ~95% |
| 1996–2010 | Lap times, pit stops, results | ~90% |
| 1950–1995 | Race results, grid positions | ~80% |

*Data sourced from FastF1 library which aggregates official F1 data sources.*

## 📝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Coding Standards

- **Backend:** Follow PEP 8, use type hints, write docstrings
- **Frontend:** Use TypeScript, follow ESLint config, use meaningful component names
- **Git:** Use conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`

## 🤝 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/yourusername/f1_race_replay_web/issues)
- Check existing issues and discussions first
- Provide detailed reproduction steps for bugs

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Non-commercial use of F1 data is generally permitted for educational and research purposes. For commercial use, please consult with official F1/FIA sources.

## 🙏 Acknowledgments

- **FastF1** - F1 data library
- **F1 Community** - Enthusiasts and data providers
- **Open Source Community** - For amazing tools and libraries

---

**Made with ❤️ by F1 enthusiasts**
