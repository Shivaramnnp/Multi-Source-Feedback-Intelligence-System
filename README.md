# Feedback Intelligence System

A production-ready full-stack application for collecting, managing, and analyzing feedback with real-time dashboards and analytics.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Features

- **Feedback Management** — Create, read, update, and delete feedback entries with rich metadata
- **Interactive Dashboard** — Real-time analytics with charts for sentiment, category, priority, and status distribution
- **Smart Filtering** — Filter feedback by category, sentiment, priority, and status
- **Pagination** — Efficient data loading with server-side pagination
- **JWT Authentication** — Secure API endpoints with token-based authentication
- **Responsive Design** — Premium dark-themed UI that works on all devices
- **Docker Support** — One-command deployment with Docker Compose
- **API Documentation** — Auto-generated Swagger/OpenAPI docs

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Frontend   | React, TypeScript, TailwindCSS v3 |
| Charts     | Recharts                          |
| Backend    | FastAPI, Python 3.12              |
| ORM        | SQLAlchemy 2.0 (async)            |
| Database   | PostgreSQL 16                     |
| Auth       | JWT (python-jose)                 |
| Container  | Docker & Docker Compose           |

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL   │
│  React + TS  │◀────│   FastAPI    │◀────│    Database    │
│  :5173 / :80 │     │    :8000     │     │    :5432      │
└─────────────┘     └──────────────┘     └──────────────┘
```

The backend follows **clean architecture** with a clear separation of concerns:

```
API Routes → Services → Repositories → Database
```

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone and start all services
docker compose up -d

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs
```

### Manual Setup

#### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Start the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start dev server
npm run dev
```

## API Endpoints

| Method   | Endpoint                        | Description            |
|----------|---------------------------------|------------------------|
| `POST`   | `/auth/login`                   | Get JWT token          |
| `POST`   | `/api/v1/feedback`              | Create feedback        |
| `GET`    | `/api/v1/feedback`              | List feedback          |
| `GET`    | `/api/v1/feedback/{id}`         | Get feedback by ID     |
| `PUT`    | `/api/v1/feedback/{id}`         | Update feedback        |
| `DELETE` | `/api/v1/feedback/{id}`         | Delete feedback        |
| `GET`    | `/api/v1/feedback/stats/summary`| Dashboard statistics   |

### Demo Credentials

```
Username: admin
Password: admin123
```

## Environment Variables

| Variable                 | Default                                              | Description              |
|--------------------------|------------------------------------------------------|--------------------------|
| `DATABASE_URL`           | `postgresql+asyncpg://postgres:postgres@localhost:5432/feedback_db` | Database connection URL  |
| `JWT_SECRET`             | —                                                    | JWT signing secret       |
| `JWT_ALGORITHM`          | `HS256`                                              | JWT algorithm            |
| `JWT_EXPIRATION_MINUTES` | `30`                                                 | Token expiration time    |
| `CORS_ORIGINS`           | `http://localhost:5173`                               | Allowed CORS origins     |
| `LOG_LEVEL`              | `INFO`                                               | Logging level            |
| `VITE_API_URL`           | `http://localhost:8000/api/v1`                        | Frontend API base URL    |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── auth/         # JWT authentication
│   │   ├── exceptions/   # Custom exception handlers
│   │   ├── middleware/    # Request logging
│   │   ├── models/       # SQLAlchemy models
│   │   ├── repositories/ # Data access layer
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── config.py     # App configuration
│   │   ├── database.py   # DB connection
│   │   └── main.py       # App entry point
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── types/        # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## License

MIT
# Intelligent-Resume-Analyzer
# Multi-Source-Feedback-Intelligence-System

# Youtube : https://www.youtube.com/watch?v=86RavYaDUyo
# LinkedIn: https://www.linkedin.com/in/shivaramnnp/
