# Flagger - Geography Education Platform

🌍 **Learn world geography through engaging, competitive games**

## Overview

Flagger is a fullstack web application that makes learning geography fun and interactive. Test your knowledge of world flags, countries, and capitals through three engaging game modes, compete on leaderboards, and challenge your friends!

### Features

- **3 Game Modes**: Flag→Country, Country→Capital, Capital→Country
- **Smart Autocomplete**: Intelligent suggestion system with prefix matching
- **Competitive Scoring**: Speed bonuses, streak multipliers, and competitive leaderboards
- **Social Features**: Friend system, leaderboards, and user profiles
- **Regional Filtering**: Focus on specific continents or play worldwide
- **Modern UI**: Beautiful, responsive interface with smooth animations

## Technology Stack

**Frontend:**
- React 18 + TypeScript + Vite
- Material-UI v5
- TanStack Query (data fetching)
- Axios (API client)

**Backend:**
- FastAPI (Python 3.11+)
- SQLAlchemy (async ORM)
- PostgreSQL 15
- Redis (caching)
- JWT Authentication

**Infrastructure:**
- Docker Compose for local development
- Alembic (database migrations)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd the-flagger
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your settings if needed (defaults work for local development).

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

4. **Run database migrations**
   
   In a new terminal:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Seed country data** (optional, required for game functionality)
   ```bash
   docker-compose exec backend python scripts/seed_countries.py
   ```

6. **Access the application**
   
   Open your browser to http://localhost:3000

## Development

### Backend Development

```bash
# Access backend container
docker-compose exec backend bash

# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Run tests
pytest
```

### Frontend Development

```bash
# Access frontend container
docker-compose exec frontend sh

# Install new package
npm install <package-name>

# Run linter
npm run lint
```

### Database Management

```bash
# Access PostgreSQL
docker-compose exec db psql -U flagger -d flagger

# Backup database
docker-compose exec db pg_dump -U flagger flagger > backup.sql

# Restore database
docker-compose exec -T db psql -U flagger flagger < backup.sql
```

## Project Structure

```
the-flagger/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core utilities (config, database, security)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── utils/             # Helper utilities
│   ├── alembic/               # Database migrations
│   ├── scripts/               # Utility scripts
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/               # API client
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom hooks
│   │   ├── pages/             # Page components
│   │   ├── types/             # TypeScript types
│   │   └── utils/             # Utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Game Modes

### Flag to Country
See a country's flag and identify the country name.

### Country to Capital
See a country name and identify its capital city.

### Capital to Country
See a capital city and identify which country it belongs to.

## Scoring System

- **Correct Answer**: 100 base points
- **Speed Bonus** (< 5 seconds): +50 points
- **Speed Bonus** (< 10 seconds): +25 points
- **Streak Bonus** (3+ correct): +10 points per streak count
- **Incorrect Answer**: 0 points, streak resets

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Contributing

This is a learning project. Contributions, issues, and feature requests are welcome!

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Country data from [REST Countries API](https://restcountries.com)
- Flag images from [FlagCDN](https://flagcdn.com)
- Icons from [Material-UI Icons](https://mui.com/material-ui/material-icons/)

---

Built with ❤️ for geography enthusiasts worldwide
