# AI Freelance Vetting App

An AI-powered freelance job search and client vetting platform that helps freelancers find safe, legitimate projects and vet clients before accepting work. Built with FastAPI, PostgreSQL, and Groq AI.

**Status:** Early Development (v0.1.0) | **Language:** Python 3.11+ | **License:** MIT

---

## Table of Contents

- [Features](#features)
- [Project Overview](#project-overview)
- [Quick Start](#quick-start)
  - [Docker Setup (Recommended)](#docker-setup-recommended)
  - [Local Development Setup](#local-development-setup)
- [Installation Instructions](#installation-instructions)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
  - [Authentication Endpoints](#authentication-endpoints)
  - [Job Search Endpoints](#job-search-endpoints)
  - [Client Vetting Endpoints](#client-vetting-endpoints-core-feature)
  - [User Endpoints](#user-endpoints)
  - [Analytics Endpoints](#analytics-endpoints)
  - [Scam Reporting Endpoints](#scam-reporting-endpoints)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Features

### Core Features (v0.1.0)

- **AI-Powered Client Vetting** - Comprehensive vetting reports powered by Groq AI
  - Trust score calculation (0-100 scale)
  - Red flag detection and risk assessment
  - Sentiment analysis of client reviews
  - AI-powered recommendations (Safe/Caution/High Risk)

- **Intelligent Job Search** - Multiple search methods
  - Advanced job filtering (budget, skills, experience level, job type)
  - Natural language AI-powered search queries
  - Job aggregation and management
  - Application tracking

- **Trust Score System** - 7-factor trust calculation
  - Account age, payment verification, total spent
  - Hire rate, average rating, response time, completion rate
  - Weighted algorithm for accurate scoring

- **Client Management**
  - Client database with detailed profiles
  - Review management and sentiment analysis
  - Red flag categorization and tracking
  - Company research capability (Premium)

- **Scam Reporting**
  - Community-driven scam reporting
  - Fraud pattern detection
  - Warning dissemination to users

- **User Management**
  - JWT-based authentication
  - Subscription tier management (Free/Pro/Premium)
  - User profile and skill management
  - Search preferences and saved searches

### Planned Features (Future)

- React frontend with Tailwind CSS
- Job scrapers for all major platforms
- Real-time job alerts via WebSocket
- Email notifications and digests
- Chrome browser extension
- Mobile app (React Native)
- Payment processing (Stripe integration)
- AI-powered cover letter generator
- Proposal analyzer and optimizer
- Community forum
- Time tracking integration
- Invoice generation

---

## Project Overview

This project is an AI-powered platform designed to solve the critical problem freelancers face: **identifying scams and vetting legitimate clients before accepting work**.

### Problem Statement

Freelancers on platforms like Upwork, Freelancer.com, and Fiverr are frequently targeted by scammers. They lose time on fake projects, payment disputes, and relationship conflicts. Current platforms have limited tools for freelancers to vet clients before accepting work.

### Solution

This platform provides:
1. **Comprehensive Client Vetting Reports** - AI-analyzed client profiles with risk assessment
2. **Trust Scoring** - Quantified client trustworthiness based on multiple factors
3. **Scam Detection** - Pattern recognition for common fraud indicators
4. **Job Matching** - Smart job discovery that filters out suspicious postings

### Architecture

```
User Interface (React Frontend)
         ↓
    REST API (FastAPI)
         ↓
Business Logic (Services)
         ↓
Database & Cache (PostgreSQL + Redis)
         ↓
External Services (Groq AI, Job Platforms)
```

---

## Quick Start

### Docker Setup (Recommended)

The easiest way to get started. Includes PostgreSQL and Redis out of the box.

#### Prerequisites

- Docker ([Install](https://docs.docker.com/get-docker/))
- Docker Compose ([Install](https://docs.docker.com/compose/install/))
- Groq API Key ([Get one here](https://console.groq.com/))

#### Steps

1. **Clone/navigate to the project:**
   ```bash
   cd /home/user/TEST/freelance_app
   ```

2. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit .env with your configuration:**
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   SECRET_KEY=generate-a-random-secret-key-here
   DEBUG=false
   ```

4. **Start the application:**
   ```bash
   docker-compose up -d
   ```

5. **Initialize the database:**
   ```bash
   docker-compose exec api python freelance_app/database/init_db.py create
   docker-compose exec api python freelance_app/database/init_db.py seed
   ```

6. **Access the application:**
   - API Docs (Swagger): http://localhost:8000/docs
   - API Docs (ReDoc): http://localhost:8000/redoc
   - API Health Check: http://localhost:8000/health

7. **View logs:**
   ```bash
   docker-compose logs -f api
   ```

8. **Stop the application:**
   ```bash
   docker-compose down
   ```

### Local Development Setup

For development without Docker. Requires PostgreSQL and Redis.

#### Prerequisites

- Python 3.11+ ([Install](https://www.python.org/downloads/))
- PostgreSQL 15+ ([Install](https://www.postgresql.org/download/))
- Redis 7+ ([Install](https://redis.io/download))
- Groq API Key

#### Steps

1. **Navigate to project:**
   ```bash
   cd /home/user/TEST/freelance_app
   ```

2. **Create Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL database:**
   ```bash
   createdb -U postgres freelance_db
   ```

5. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

6. **Configure .env:**
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/freelance_db
   REDIS_URL=redis://localhost:6379/0
   GROQ_API_KEY=your_api_key
   SECRET_KEY=your-random-secret-key
   DEBUG=true  # Enable debug mode for development
   ```

7. **Initialize database:**
   ```bash
   python freelance_app/database/init_db.py create
   python freelance_app/database/init_db.py seed
   ```

8. **Start the application:**
   ```bash
   python freelance_app/main.py
   ```

   Or with auto-reload:
   ```bash
   uvicorn freelance_app.main:app --reload --host 0.0.0.0 --port 8000
   ```

9. **Access the application:**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc Docs: http://localhost:8000/redoc

---

## Installation Instructions

### Using the Start Script

An automated setup script is provided:

```bash
bash start.sh
```

This script will:
- Check for .env file
- Ask for setup method (Docker or Local)
- Install dependencies
- Initialize database
- Provide quick access information

### Manual Installation

See [Docker Setup](#docker-setup-recommended) or [Local Development Setup](#local-development-setup) above.

### Environment Configuration

Create a `.env` file in the `/freelance_app` directory:

```env
# Application
APP_NAME=AI Freelance Search App
APP_VERSION=0.1.0
DEBUG=false

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=postgresql://freelance_user:freelance_pass@localhost:5432/freelance_db
SQL_ECHO=false

# Redis Cache
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Groq AI
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Development
DEBUG=false
```

---

## Configuration

### Application Settings

Configuration is managed through:
1. **Environment Variables** - Set in `.env` file
2. **Python Settings** - Defined in `config.py`

### Key Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | false | Enable debug mode |
| `API_HOST` | 0.0.0.0 | API server host |
| `API_PORT` | 8000 | API server port |
| `SECRET_KEY` | (required) | JWT signing key |
| `GROQ_API_KEY` | (required) | Groq API authentication |
| `DATABASE_URL` | postgres://... | PostgreSQL connection string |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection string |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 15 | JWT token expiry |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Refresh token expiry |

### Subscription Tiers

Three subscription levels control feature access:

| Feature | Free | Pro | Premium |
|---------|------|-----|---------|
| Vetting Reports/Month | 5 | Unlimited | Unlimited |
| Company Research | No | No | Yes |
| API Rate Limit | 100 req/hr | 1000 req/hr | 5000 req/hr |
| Cost | Free | TBD | TBD |

---

## API Documentation

### Base URL

```
http://localhost:8000/api
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

All protected endpoints require a Bearer token:

```
Authorization: Bearer <access_token>
```

### Authentication Endpoints

#### Register User
```
POST /auth/register

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

Response:
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "subscription_tier": "free",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Login
```
POST /auth/login

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Refresh Token
```
POST /auth/refresh

Request:
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### Get Current User
```
GET /auth/me

Headers:
Authorization: Bearer <access_token>

Response:
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "subscription_tier": "free",
  "is_active": true,
  "skills": [...],
  "preferences": {...}
}
```

### Job Search Endpoints

#### Search Jobs
```
GET /jobs?search_query=React&min_budget=50&max_hourly_rate=100

Query Parameters:
- search_query: Text search in title/description
- category: Job category filter
- job_type: hourly, fixed, both
- experience_level: entry, intermediate, expert
- min_budget: Minimum project budget
- max_budget: Maximum project budget
- min_hourly_rate: Minimum hourly rate
- max_hourly_rate: Maximum hourly rate
- skills: Required skills (comma-separated)
- is_active: Filter active/inactive jobs
- sort_by: posted_date, budget_min, hourly_rate
- sort_order: asc or desc
- page: Page number (default: 1)
- per_page: Results per page (default: 20)

Response:
{
  "total": 342,
  "page": 1,
  "per_page": 20,
  "total_pages": 18,
  "jobs": [
    {
      "id": 1,
      "title": "React Developer Needed",
      "description": "...",
      "category": "Web Development",
      "job_type": "fixed",
      "fixed_price": 500,
      "skills_required": ["React", "JavaScript"],
      "experience_level": "intermediate",
      "is_active": true,
      "posted_date": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### AI-Powered Job Search
```
POST /jobs/search/ai

Headers:
Authorization: Bearer <access_token>

Request:
{
  "search_query": "I want Python jobs paying at least $50/hour"
}

Query Parameters:
- page: Page number (default: 1)
- per_page: Results per page (default: 20)

Response:
{
  "total": 48,
  "page": 1,
  "per_page": 20,
  "total_pages": 3,
  "jobs": [...]  # AI-filtered results
}
```

#### Get Job Details
```
GET /jobs/{job_id}

Response:
{
  "id": 1,
  "title": "React Developer Needed",
  "description": "Full project description...",
  "category": "Web Development",
  "client_id": 5,
  "client": {
    "id": 5,
    "name": "John Smith",
    "company_name": "Tech Startup",
    "trust_score": 85,
    "average_rating": 4.5
  },
  ...
}
```

### Client Vetting Endpoints (Core Feature)

#### Search Clients
```
GET /clients?min_trust_score=70&sort_by=trust_score

Query Parameters:
- search_query: Search client name/company
- min_trust_score: Minimum trust score (0-100)
- max_trust_score: Maximum trust score (0-100)
- payment_verified_only: Filter verified payment
- is_verified_only: Filter verified accounts
- min_rating: Minimum rating
- sort_by: trust_score, average_rating, total_spent
- sort_order: asc or desc
- page: Page number
- per_page: Results per page

Response:
{
  "total": 150,
  "page": 1,
  "per_page": 20,
  "total_pages": 8,
  "clients": [...]
}
```

#### Get Client Vetting Report (CORE FEATURE)
```
GET /clients/{client_id}/vetting-report

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- include_ai_analysis: Include AI analysis (default: true)
- include_company_research: Include company research (Pro/Premium only)

Response:
{
  "client": {
    "id": 5,
    "name": "John Smith",
    "company_name": "Tech Startup",
    "trust_score": 85,
    "average_rating": 4.5,
    "total_spent": 15000,
    "payment_verified": true,
    "is_verified": true
  },
  "reviews": [
    {
      "id": 1,
      "reviewer_name": "Freelancer Name",
      "rating": 5,
      "review_text": "Great client to work with...",
      "project_title": "Website Redesign",
      "project_value": 1200
    }
  ],
  "red_flags": [
    {
      "id": 1,
      "flag_type": "payment_issues",
      "description": "Delayed payment for 2 projects",
      "severity": "medium"
    }
  ],
  "scam_reports": [],
  "overall_risk_score": 15,
  "recommendation": "LOW RISK - Safe to proceed",
  "summary": "This client shows positive indicators with a trust score of 85/100 and minimal red flags.",
  "report_generated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Client Details
```
GET /clients/{client_id}

Response:
{
  "id": 5,
  "name": "John Smith",
  "company_name": "Tech Startup",
  "email": "john@startup.com",
  "trust_score": 85,
  "average_rating": 4.5,
  "total_spent": 15000,
  "total_jobs_posted": 24,
  "payment_verified": true,
  "is_verified": true,
  "member_since": "2018-05-10T00:00:00Z"
}
```

#### Get Client Reviews
```
GET /clients/{client_id}/reviews?page=1&per_page=10

Response:
[
  {
    "id": 1,
    "client_id": 5,
    "reviewer_name": "Freelancer Name",
    "rating": 5,
    "review_text": "Excellent client, easy to work with...",
    "project_title": "Website Redesign",
    "project_value": 1200,
    "review_date": "2024-01-10T00:00:00Z"
  }
]
```

#### Add Client Review
```
POST /clients/{client_id}/reviews

Headers:
Authorization: Bearer <access_token>

Request:
{
  "reviewer_name": "Your Name (optional)",
  "rating": 4,
  "review_text": "Good client, professional communication...",
  "project_title": "API Development",
  "project_value": 2500
}

Response:
{
  "id": 2,
  "client_id": 5,
  "reviewer_name": "Your Name",
  "rating": 4,
  ...
}
```

#### Get Client Red Flags
```
GET /clients/{client_id}/red-flags?severity=high

Response:
[
  {
    "id": 1,
    "client_id": 5,
    "flag_type": "payment_issues",
    "description": "Client delayed payment by 2 weeks",
    "severity": "medium",
    "detected_at": "2024-01-12T10:30:00Z",
    "is_resolved": false
  }
]
```

#### Report Client Red Flag
```
POST /clients/{client_id}/red-flags

Headers:
Authorization: Bearer <access_token>

Request:
{
  "flag_type": "communication_issues",
  "description": "Client not responsive for 5 days",
  "severity": "high"
}

Response:
{
  "id": 2,
  "client_id": 5,
  "flag_type": "communication_issues",
  ...
}
```

### User Endpoints

#### Get User Profile
```
GET /users/me

Headers:
Authorization: Bearer <access_token>

Response:
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "subscription_tier": "free",
  "is_active": true,
  "skills": ["Python", "React", "PostgreSQL"],
  "preferences": {...}
}
```

#### Update User Profile
```
PUT /users/me

Headers:
Authorization: Bearer <access_token>

Request:
{
  "full_name": "John Doe Updated",
  "bio": "Experienced freelancer...",
  "portfolio_url": "https://..."
}
```

### Analytics Endpoints

#### Get User Analytics
```
GET /analytics/me

Headers:
Authorization: Bearer <access_token>

Response:
{
  "user_id": 1,
  "total_jobs_applied": 15,
  "total_jobs_hired": 3,
  "total_earnings": 8500,
  "average_project_value": 2833,
  "success_rate": 20,
  "last_30_days": {
    "applications": 5,
    "hires": 1,
    "earnings": 2500
  }
}
```

### Scam Reporting Endpoints

#### Report Scam
```
POST /scam-reports

Headers:
Authorization: Bearer <access_token>

Request:
{
  "client_id": 5,
  "job_id": 123,
  "description": "Client requested payment upfront...",
  "scam_type": "payment_upfront",
  "severity": "high"
}

Response:
{
  "id": 1,
  "client_id": 5,
  "reported_by_user_id": 1,
  "description": "...",
  "scam_type": "payment_upfront",
  "severity": "high",
  "is_verified": false,
  "reported_at": "2024-01-15T10:30:00Z"
}
```

#### Get Scam Reports
```
GET /scam-reports?client_id=5

Response:
[
  {
    "id": 1,
    "client_id": 5,
    "description": "...",
    "scam_type": "payment_upfront",
    "severity": "high",
    "report_count": 3,
    "reported_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│         React.js + Tailwind CSS (Future)                │
└─────────────────────────────────────────────────────────┘
                       ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   Backend API Layer                      │
│              FastAPI + Python 3.11+                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Auth Service  │  Job Service  │  Vetting Service│   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                 Business Logic Layer                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │  AI Service (Groq Integration)                   │  │
│  │  Trust Score Service                             │  │
│  │  Vetting Service                                 │  │
│  │  Job Scraping Service (Future)                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│                     Data Layer                           │
│  ┌──────────────┬──────────────┬──────────────────┐    │
│  │  PostgreSQL  │    Redis     │   File Storage   │    │
│  │  (Primary DB)│   (Cache)    │   (Images/Docs)  │    │
│  └──────────────┴──────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Key Services

#### 1. Authentication Service
- JWT token generation and validation
- Password hashing with bcrypt
- User registration and login
- Token refresh mechanism

#### 2. AI Service (Groq Integration)
- Natural language query processing
- Sentiment analysis of reviews
- Red flag detection patterns
- Company research and verification
- Recommendation generation

#### 3. Trust Score Service
7-factor weighted algorithm:
- Account age (20%)
- Payment verification (15%)
- Total spent (15%)
- Hire rate (15%)
- Average rating (20%)
- Response time (10%)
- Completion rate (5%)

#### 4. Vetting Service (CORE)
Combines all data sources for comprehensive client assessment:
- Client basic information
- Historical job data
- Trust score calculation
- AI-powered analysis
- Risk assessment and recommendations

#### 5. Job Service
- Job search with advanced filtering
- Job aggregation
- Application tracking
- AI-powered job matching

### Database Schema

14 tables organized by function:

**User Management:**
- `users` - User accounts
- `user_skills` - User skills
- `user_preferences` - Search preferences

**Job Management:**
- `freelance_platforms` - Supported platforms
- `jobs` - Job listings
- `job_applications` - User applications

**Client Management:**
- `clients` - Client profiles
- `client_reviews` - Freelancer reviews
- `client_red_flags` - Warning signs
- `company_research` - Company verification

**Analytics & Safety:**
- `saved_searches` - User's saved searches
- `user_analytics` - User success metrics
- `scam_reports` - Community reports

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.11+ |
| **API Framework** | FastAPI | 0.109+ |
| **Web Server** | Uvicorn | 0.27+ |
| **Database** | PostgreSQL | 15+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Caching** | Redis | 7.0+ |
| **Task Queue** | Celery | 5.3+ (Future) |
| **AI Engine** | Groq API | Latest |
| **Authentication** | JWT + Bcrypt | - |
| **Validation** | Pydantic | 2.5+ |
| **HTTP Client** | HTTPX/Requests | - |
| **Scraping** | BeautifulSoup4 + Selenium | - |
| **Testing** | Pytest | 7.4+ |
| **Code Quality** | Black, Flake8, MyPy | Latest |
| **Deployment** | Docker + Docker Compose | Latest |
| **Frontend (Future)** | React | 18+ |
| **Styling (Future)** | Tailwind CSS | Latest |

### Python Dependencies

Key packages included in `requirements.txt`:

```
fastapi==0.109.2
uvicorn==0.27.1
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.6
python-jose==3.3.0
passlib==1.7.4
pydantic==2.5.3
groq==0.4.2
pytest==7.4.4
black==24.1.1
flake8==7.0.0
```

---

## Usage Examples

### Example 1: User Registration and Authentication

```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "freelancer@example.com",
    "password": "SecurePass123!",
    "full_name": "Jane Developer"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "freelancer@example.com",
    "password": "SecurePass123!"
  }'

# Save the returned access_token for subsequent requests
```

### Example 2: Search Jobs and Apply

```bash
# Search for React jobs with minimum $50/hour
curl -X GET "http://localhost:8000/jobs?search_query=React&min_hourly_rate=50&skills=React" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Apply to a job
curl -X POST "http://localhost:8000/jobs/applications" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 123,
    "proposal_text": "I have 5 years of React experience...",
    "bid_amount": 55
  }'
```

### Example 3: Generate Client Vetting Report (CORE FEATURE)

```bash
# Get comprehensive vetting report for a client
curl -X GET "http://localhost:8000/clients/5/vetting-report" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response includes trust score, red flags, AI recommendations
# Risk assessment: LOW RISK, MEDIUM RISK, or HIGH RISK
```

### Example 4: AI-Powered Job Search

```bash
# Natural language job search
curl -X POST "http://localhost:8000/jobs/search/ai" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "search_query": "I want Python backend jobs paying more than $60/hour, under 30 hours/week"
  }'

# AI interprets the query and returns filtered results
```

### Example 5: Community Scam Reporting

```bash
# Report a scam
curl -X POST "http://localhost:8000/scam-reports" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 42,
    "description": "Requested payment through non-platform method...",
    "scam_type": "payment_upfront",
    "severity": "high"
  }'

# Get scam reports for a client
curl -X GET "http://localhost:8000/scam-reports?client_id=42" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=freelance_app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_auth.py::test_user_registration
```

### Test Structure

```
tests/
├── test_auth.py           # Authentication tests
├── test_jobs.py           # Job search tests
├── test_clients.py        # Client vetting tests
├── test_users.py          # User management tests
├── test_analytics.py      # Analytics tests
└── conftest.py            # Pytest configuration
```

### Test Examples

```python
# tests/test_auth.py
def test_user_registration(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_user_login(client, test_user):
    response = client.post("/auth/login", json={
        "email": test_user.email,
        "password": "TestPass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Running Linters

```bash
# Format code with Black
black freelance_app/

# Check code style with Flake8
flake8 freelance_app/

# Type checking with MyPy
mypy freelance_app/
```

---

## Deployment

### Docker Deployment

The application is containerized and ready for deployment.

#### Docker Compose (Development)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Production Deployment

For production, consider:

1. **Container Registry** - Push to DockerHub, GCR, or ECR
2. **Orchestration** - Deploy with Kubernetes, ECS, or Cloud Run
3. **Database** - Use managed PostgreSQL (RDS, Cloud SQL)
4. **Caching** - Use managed Redis (ElastiCache, MemoryStore)
5. **CDN** - CloudFront or Cloudflare for static assets
6. **Monitoring** - Set up CloudWatch, Datadog, or New Relic
7. **Load Balancing** - Use ALB, NLB, or cloud load balancer

#### Environment Variables for Production

```env
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=<generate-strong-secret>
GROQ_API_KEY=<your-api-key>
DATABASE_URL=<managed-database-url>
REDIS_URL=<managed-redis-url>
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

### CI/CD Pipeline

Recommended GitHub Actions workflow:

```yaml
name: Test and Deploy

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: black --check freelance_app/
      - run: flake8 freelance_app/
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error:** `Could not connect to server: Connection refused`

**Solution:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify PostgreSQL credentials

```bash
# Test PostgreSQL connection
psql -U freelance_user -d freelance_db -h localhost
```

#### 2. Redis Connection Error

**Error:** `ConnectionError: Error 111 connecting to localhost:6379`

**Solution:**
- Ensure Redis is running
- Check REDIS_URL in .env
- Verify Redis port

```bash
# Test Redis connection
redis-cli ping
# Should return: PONG
```

#### 3. Groq API Key Error

**Error:** `Invalid API key` or `Authentication failed`

**Solution:**
- Verify GROQ_API_KEY in .env
- Get a new key from https://console.groq.com/
- Ensure key has necessary permissions

#### 4. Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn freelance_app.main:app --port 8001
```

#### 5. Docker Build Failure

**Error:** `Build failed` or `Dependency installation failed`

**Solution:**
```bash
# Clean and rebuild
docker-compose down
docker system prune -a
docker-compose build --no-cache
docker-compose up
```

### Debug Mode

Enable detailed logging:

```env
DEBUG=true
```

View logs:
```bash
# Docker
docker-compose logs -f api

# Local
# Set DEBUG=true in .env, logs appear in console
```

### Health Check

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy"}
```

---

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/my-feature`
3. **Install dev dependencies:** `pip install -r requirements.txt`
4. **Make changes and test:** `pytest`
5. **Format code:** `black freelance_app/`
6. **Lint code:** `flake8 freelance_app/`
7. **Type check:** `mypy freelance_app/`
8. **Commit:** `git commit -m "Add my feature"`
9. **Push:** `git push origin feature/my-feature`
10. **Create Pull Request**

### Code Standards

- **Style:** Black formatter
- **Linting:** Flake8
- **Type Hints:** MyPy
- **Testing:** Pytest with >80% coverage
- **Docstrings:** Google style

### Commit Messages

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add tests
refactor: Refactor code
style: Format code
```

---

## Support

- **Documentation:** See `/home/user/TEST/freelance_app/ARCHITECTURE.md`
- **API Docs:** http://localhost:8000/docs
- **Issues:** Report via GitHub Issues
- **Email:** support@example.com

---

## License

MIT License - See LICENSE file for details

---

## Changelog

### Version 0.1.0 (Current)

- Initial release
- Authentication system (JWT)
- Job search with advanced filtering
- Client vetting reports (CORE FEATURE)
- Trust score algorithm
- Scam reporting
- User management
- API documentation

---

**Last Updated:** January 17, 2024
**Project Status:** Early Development (v0.1.0)
**Python Version:** 3.11+
