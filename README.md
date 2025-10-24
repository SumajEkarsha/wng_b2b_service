# School Mental Health Platform - Backend Service

FastAPI + SQLAlchemy + PostgreSQL (Neon DB) backend for the School Mental Health SaaS platform.

## Tech Stack
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Neon DB serverless Postgres
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **JWT**: Authentication

## Quick Start

### Option 1: Local Development with Neon DB

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your Neon DB connection string:
```
DATABASE_URL=postgresql://user:password@your-neon-host/dbname
SECRET_KEY=your-secret-key-change-this
```

3. **Initialize database:**
```bash
python scripts/init_db.py
```

4. **Start the server:**
```bash
uvicorn app.main:app --reload
```

5. **Access the API:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Option 2: Docker Compose (Local PostgreSQL)

1. **Start services:**
```bash
docker-compose up -d
```

2. **Initialize database:**
```bash
docker-compose exec api python scripts/init_db.py
```

3. **Access the API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Database Migrations

### Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login and get JWT token

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PATCH /api/v1/users/{user_id}` - Update user

### Students
- `POST /api/v1/students/` - Create student
- `GET /api/v1/students/` - List students
- `GET /api/v1/students/{student_id}` - Get student
- `PATCH /api/v1/students/{student_id}` - Update student

### Cases
- `POST /api/v1/cases/` - Create case
- `GET /api/v1/cases/` - List cases
- `GET /api/v1/cases/{case_id}` - Get case
- `POST /api/v1/cases/{case_id}/journal` - Add journal entry
- `GET /api/v1/cases/{case_id}/journal` - Get journal entries

### Observations
- `POST /api/v1/observations/` - Create observation
- `GET /api/v1/observations/` - List observations
- `GET /api/v1/observations/{observation_id}` - Get observation

### Assessments
- `POST /api/v1/assessments/` - Create assessment
- `POST /api/v1/assessments/{id}/submit` - Submit responses
- `GET /api/v1/assessments/{id}/score` - Get scores
- `GET /api/v1/assessments/` - List assessments

### Consents
- `POST /api/v1/consents/` - Create consent
- `GET /api/v1/consents/` - List consents
- `POST /api/v1/consents/{id}/revoke` - Revoke consent

## Sample Credentials (after init_db.py)

```
Counsellor: counsellor@demo.school / password123
Teacher: teacher@demo.school / password123
Principal: principal@demo.school / password123
```

## Project Structure
```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/    # API route handlers
│   │   └── __init__.py
│   └── dependencies.py   # Shared dependencies
├── core/
│   ├── config.py         # Settings
│   ├── database.py       # DB connection
│   └── security.py       # Auth utilities
├── models/               # SQLAlchemy models
│   ├── user.py
│   ├── student.py
│   ├── case.py
│   ├── assessment.py
│   ├── observation.py
│   └── consent.py
├── schemas/              # Pydantic schemas
│   ├── user.py
│   ├── student.py
│   ├── case.py
│   └── ...
└── main.py              # Application entry point

alembic/                 # Database migrations
scripts/                 # Utility scripts
```

## Development

### Run tests:
```bash
pytest
```

### Format code:
```bash
black app/
```

### Lint:
```bash
flake8 app/
```

## Deployment

### Neon DB Setup
1. Create a Neon project at https://neon.tech
2. Copy the connection string
3. Update DATABASE_URL in your environment

### Environment Variables
Required for production:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Strong random key for JWT
- `ENVIRONMENT`: Set to "production"

## Security Features
- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Consent management
- Audit logging ready

## Next Steps
- Add AI integration endpoints
- Implement dashboard analytics
- Add real-time notifications
- Integrate with external services
- Add comprehensive test coverage
