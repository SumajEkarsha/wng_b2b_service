# WellNest Group - School Mental Wellness Platform (Backend)

**A comprehensive mental health and wellbeing management system for educational institutions.**

## 🎯 Overview

FastAPI-based backend service powering the WellNest Group platform. This system enables schools to track student wellbeing, manage counseling cases, conduct assessments, and provide data-driven insights to support student mental health.

## ✨ Key Features

- **Student Wellbeing Tracking**: Monitor student mental health through assessments and observations
- **Case Management**: Complete counseling case lifecycle management with journaling
- **Assessment System**: Customizable mental health assessments with automated scoring
- **Multi-Role Support**: Purpose-built dashboards for Teachers, Counsellors, and Principals
- **Calendar & Scheduling**: Session booking and calendar management
- **Activity Monitoring**: Track student participation in wellbeing activities
- **Resource Library**: Curated mental health resources and webinars
- **Marketplace**: Connect with external therapists and book sessions
- **AI-Powered Insights**: Smart analytics and recommendations
- **Consent Management**: GDPR-compliant consent tracking

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | High-performance async web framework |
| **SQLAlchemy** | ORM for database operations |
| **PostgreSQL** | Primary database (Neon DB) |
| **Alembic** | Database schema migrations |
| **Pydantic** | Data validation and serialization |
| **JWT** | Secure authentication |
| **Bcrypt** | Password hashing |

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (or Neon DB account)
- pip or uv package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd wng_b2b_service
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` and set:
```env
DATABASE_URL=postgresql://user:password@host/dbname
SECRET_KEY=your-super-secret-key-change-this
ENVIRONMENT=development
```

4. **Run database migrations**
```bash
alembic upgrade head
```

5. **Start the server**
```bash
uvicorn app.main:app --reload
```

6. **Access the API**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## 📁 Project Structure

```
app/
├── api/v1/endpoints/     # API route handlers
│   ├── auth.py
│   ├── users.py
│   ├── students.py
│   ├── cases.py
│   ├── assessments.py
│   └── ...
├── core/                 # Core configurations
│   ├── config.py
│   ├── database.py
│   └── security.py
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── crud/                # Database operations
└── main.py             # Application entry

alembic/                # Database migrations
scripts/                # Utility scripts
```

## 🔑 Authentication

The API uses JWT-based authentication. Include the token in requests:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users/me
```

### Login
```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

## 📚 API Documentation

### Core Endpoints

**Authentication**
- `POST /api/v1/auth/login` - User login

**Users & Profiles**
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/{id}` - Update user profile

**Students**
- `GET /api/v1/students/` - List students (filtered by role)
- `GET /api/v1/students/{id}` - Get student details
- `POST /api/v1/students/` - Create student

**Cases**
- `GET /api/v1/cases/` - List cases
- `POST /api/v1/cases/` - Create new case
- `GET /api/v1/cases/{id}` - Get case details
- `POST /api/v1/cases/{id}/journal` - Add journal entry

**Assessments**
- `GET /api/v1/assessments/` - List assessments
- `POST /api/v1/assessments/` - Create assessment
- `POST /api/v1/assessments/{id}/submit` - Submit responses
- `GET /api/v1/assessments/{id}/score` - Get scores

**Calendar & Sessions**
- `GET /api/v1/calendar/` - Get calendar events
- `POST /api/v1/calendar/` - Create event
- `PATCH /api/v1/calendar/{id}` - Update event

**Analytics**
- `GET /api/v1/analytics/school` - School-wide analytics
- `GET /api/v1/analytics/teacher` - Teacher dashboard data
- `GET /api/v1/analytics/counsellor` - Counsellor dashboard data

For complete API documentation, visit `/docs` when running the server.

## 🗄️ Database Migrations

**Create a new migration**
```bash
alembic revision --autogenerate -m "Add new column"
```

**Apply migrations**
```bash
alembic upgrade head
```

**Rollback**
```bash
alembic downgrade -1
```

**View migration history**
```bash
alembic history
```

## 🔒 Security Features

- JWT token authentication with configurable expiry
- Password hashing using bcrypt
- Role-based access control (RBAC)
- Consent management for data privacy
- SQL injection protection via SQLAlchemy
- CORS configuration for frontend integration

## 🧪 Development

### Code Quality
```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

### Running Tests
```bash
pytest
pytest --cov=app tests/
```

## 🌍 Deployment

### Environment Variables

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Strong random key for JWT signing

**Optional:**
- `ENVIRONMENT` - Set to `production`
- `CORS_ORIGINS` - Allowed CORS origins
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT expiry (default: 30)

### Neon DB Setup
1. Create project at https://neon.tech
2. Copy connection string
3. Update `DATABASE_URL` in environment

### Docker Deployment
```bash
docker build -t wellnest-backend .
docker run -p 8000:8000 --env-file .env wellnest-backend
```

## 📊 Database Schema

Key entities:
- **Users**: Teachers, Counsellors, Principals
- **Students**: Student profiles with wellbeing data
- **Cases**: Counseling cases with risk levels
- **Assessments**: Mental health assessment templates
- **Observations**: Teacher/staff observations
- **Consents**: Parent/guardian consent records
- **Calendar**: Events and session bookings
- **Activities**: Wellbeing activities and workshops

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

Proprietary - WellNest Group © 2024

## 🆘 Support

For issues or questions, contact: support@wellnestgroup.com
