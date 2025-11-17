# AI Freelance Search App - Architecture Design

## System Overview

The AI Freelance Search App is built on top of the Groq MCP Server infrastructure, leveraging Groq's AI capabilities for intelligent job search, client vetting, and fraud detection.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│         React.js + Tailwind CSS + Chart.js              │
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
│  │  - Chat Completion (groq_ttt.py)                 │  │
│  │  - Compound Beta (groq_compound.py)              │  │
│  │  - Vision (groq_vision.py)                       │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  Trust Score Service                             │  │
│  │  - Calculate 0-100 score based on 7 factors      │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  Vetting Service                                 │  │
│  │  - Generate comprehensive client reports         │  │
│  │  - Red flag detection                            │  │
│  │  - Sentiment analysis                            │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  Job Scraping Service                            │  │
│  │  - Upwork, Freelancer, Fiverr, Guru scrapers     │  │
│  ├──────────────────────────────────────────────────┤  │
│  │  Alert Service (Celery)                          │  │
│  │  - Match jobs to saved searches                  │  │
│  │  - Send notifications                            │  │
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

## Component Details

### 1. Frontend Layer (Future Implementation)

**Technology**: React.js with Tailwind CSS

**Features**:
- Job search interface with advanced filters
- Client vetting report viewer
- User dashboard with analytics
- Saved searches management
- Dark mode support

**Components**:
- `JobSearchPage`: Search and filter jobs
- `VettingReportPage`: Display client vetting reports
- `DashboardPage`: User analytics and insights
- `SettingsPage`: User preferences and subscriptions

### 2. Backend API Layer

**Technology**: FastAPI (Python 3.11+)

**API Routers**:
- `/api/auth`: Authentication and user management
- `/api/users`: User profiles, skills, preferences
- `/api/jobs`: Job search, listings, applications
- `/api/clients`: Client vetting and reports
- `/api/analytics`: User and market analytics
- `/api/scam-reports`: Community scam reporting

**Key Features**:
- RESTful API design
- JWT authentication with refresh tokens
- Request validation with Pydantic
- Auto-generated API documentation (Swagger/ReDoc)
- CORS support for frontend integration
- Rate limiting (to be implemented)

### 3. Business Logic Layer

#### 3.1 AI Service

**Integration with Groq MCP Server**:
```python
from src.groq_ttt import chat_completion
from src.groq_compound import compound_tool
```

**Capabilities**:
1. **Sentiment Analysis**: Analyze client reviews
2. **Theme Extraction**: Extract common patterns from feedback
3. **Red Flag Detection**: Identify suspicious patterns
4. **Company Research**: Use compound-beta for web research
5. **Natural Language Search**: Parse user search queries
6. **Job Description Summarization**: Extract key points

**Models Used**:
- Primary: `llama-3.3-70b-versatile`
- Compound: `compound-beta` (for multi-agent research)

#### 3.2 Trust Score Service

**Algorithm**: Calculate client trustworthiness (0-100)

**Factors**:
1. **Account Age** (20 points): Older = more trustworthy
2. **Payment Verification** (15 points): Verified payment method
3. **Total Spent** (15 points): Higher spending = commitment
4. **Hire Rate** (15 points): Ratio of hires to postings
5. **Average Rating** (20 points): Client feedback scores
6. **Response Time** (10 points): How quickly they respond
7. **Completion Rate** (5 points): Project completion success

**Thresholds**:
- 80-100: Excellent (Proceed with confidence)
- 60-79: Good (Generally safe)
- 40-59: Average (Exercise caution)
- 20-39: Below Average (High risk)
- 0-19: Poor (Avoid)

#### 3.3 Vetting Service

**Core Feature**: Generate comprehensive client vetting reports

**Report Components**:
1. **Trust Score**: 0-100 with star rating
2. **Strengths**: Positive client attributes
3. **Concerns**: Yellow flags to watch
4. **Red Flags**: Critical warning signs
5. **Hiring History**: Stats and timeline
6. **Review Analysis**: Sentiment and themes
7. **Company Research**: LinkedIn, website, social media
8. **AI Recommendation**: Safe to proceed or avoid

**Red Flags Detected**:
- New account with no history
- Suspiciously high pay for simple tasks
- Pattern of cancelled projects
- Off-platform communication requests
- Fake review patterns
- Payment issues reported
- Account verification problems

#### 3.4 Job Scraping Service (To Be Implemented)

**Platforms**:
- Upwork (API + scraping)
- Freelancer (scraping)
- Fiverr (scraping)
- Guru (scraping)
- PeoplePerHour (scraping)

**Data Collected**:
- Job title and description
- Budget/hourly rate
- Skills required
- Client information
- Post date
- Number of proposals
- Project duration

**Scraping Strategy**:
- Respect robots.txt
- Rate limiting
- User-agent rotation
- Error handling and retries
- Incremental updates (scrape new jobs only)

### 4. Data Layer

#### 4.1 PostgreSQL Database

**Schema Overview** (14 tables):

**Users & Preferences**:
- `users`: User accounts
- `user_skills`: Skills they offer
- `user_preferences`: Search preferences

**Platforms & Jobs**:
- `freelance_platforms`: Platform definitions
- `jobs`: Job listings
- `job_applications`: User applications

**Clients & Vetting**:
- `clients`: Client profiles
- `client_reviews`: Freelancer feedback
- `client_red_flags`: Warning signs
- `company_research`: Company verification data

**Search & Analytics**:
- `saved_searches`: User's saved search criteria
- `user_analytics`: User success metrics
- `platform_analytics`: Market insights

**Safety**:
- `scam_reports`: Community-reported scams

**Key Design Decisions**:
- Use JSONB for flexible data (metadata, filters)
- Foreign keys with cascade deletes
- Indexes on frequently queried columns
- `created_at`/`updated_at` timestamps on all tables

#### 4.2 Redis

**Use Cases**:
- API response caching (5-minute TTL for job listings)
- User session storage
- Rate limiting counters
- Celery task queue backend

#### 4.3 File Storage (Future)

**Storage**: AWS S3 or local filesystem

**Files**:
- User profile pictures
- Company logos
- Scraped job data archives
- Vetting report PDFs (for premium users)

### 5. External Integrations

#### 5.1 Groq API

**Endpoints Used**:
- Chat Completions: `https://api.groq.com/openai/v1/chat/completions`
- Compound Beta: Custom multi-agent endpoint

**Rate Limits**: Respect Groq's rate limits with backoff

#### 5.2 Freelance Platforms

**API Access** (where available):
- Upwork: OAuth2 API access

**Web Scraping** (ethical):
- Respect robots.txt
- Rate limiting (1 req/sec)
- Clear User-Agent
- No CAPTCHA bypass

#### 5.3 Email Service (Future)

**Provider**: SendGrid or AWS SES

**Use Cases**:
- Account verification
- Job alerts
- Scam warnings
- Weekly digests

## Data Flow Examples

### Example 1: Client Vetting Report Generation

```
1. User requests vetting report for client_id=123
   ↓
2. API validates user has sufficient subscription tier
   ↓
3. VettingService.generate_report(client_id=123)
   ↓
4. Fetch client data from database
   ↓
5. TrustScoreService.calculate_score(client)
   ↓
6. AIService.detect_red_flags(client_history)
   ↓
7. AIService.analyze_review_sentiment(reviews)
   ↓
8. AIService.extract_review_themes(reviews)
   ↓
9. AIService.research_company(client.company_name) [compound-beta]
   ↓
10. Combine all data into vetting report
   ↓
11. Return JSON response to user
```

### Example 2: AI-Powered Job Search

```
1. User enters: "find React jobs paying $50+/hour"
   ↓
2. AIService.parse_natural_language_query(query)
   ↓
3. Extract: skills=["React"], min_hourly_rate=50
   ↓
4. Query database with filters
   ↓
5. For each job:
     - Fetch client data
     - Calculate trust score (cached if available)
   ↓
6. Sort by relevance and trust score
   ↓
7. Return paginated results with client vetting summaries
```

### Example 3: Job Alert System

```
1. Celery periodic task runs every 15 minutes
   ↓
2. Fetch all active saved searches
   ↓
3. For each saved search:
     a. Query new jobs matching criteria
     b. If matches found:
        - Generate job summary
        - Send notification (email/push)
        - Mark jobs as "alerted"
   ↓
4. Update last_checked timestamp
```

## Security Architecture

### Authentication & Authorization

**JWT Tokens**:
- Access token: 15-minute expiry
- Refresh token: 7-day expiry
- Secure HTTP-only cookies for web

**Password Security**:
- Bcrypt hashing (cost factor 12)
- Minimum 8 characters
- Complexity requirements

**2FA** (Future):
- TOTP (Time-based One-Time Password)
- SMS backup codes

### Data Protection

**Encryption**:
- At rest: PostgreSQL encryption
- In transit: HTTPS/TLS 1.3
- Sensitive fields: Additional encryption for payment data

**Access Control**:
- Role-based access (user, admin)
- Subscription tier enforcement
- API rate limiting per user

### API Security

**Rate Limiting**:
- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Premium tier: 5000 requests/hour

**Input Validation**:
- Pydantic schemas for all inputs
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (sanitize outputs)

**CORS**:
- Whitelist allowed origins
- Credentials support for cookies

## Scalability Considerations

### Horizontal Scaling

**Stateless API**:
- No server-side sessions (JWT tokens)
- Can scale web servers horizontally
- Load balancer distributes traffic

**Database**:
- PostgreSQL read replicas for scaling reads
- Write operations to primary
- Connection pooling (SQLAlchemy)

**Caching**:
- Redis for frequently accessed data
- Reduce database load
- Can scale Redis with clustering

### Performance Optimization

**Database Optimizations**:
- Indexes on foreign keys and search fields
- Materialized views for analytics
- Pagination for large result sets
- Query optimization (explain analyze)

**API Optimizations**:
- Response compression (gzip)
- Pagination on list endpoints
- Field selection (return only needed fields)
- Async processing for long tasks (Celery)

**Caching Strategy**:
- Client vetting reports: 1-hour cache
- Job listings: 5-minute cache
- User profiles: 30-minute cache
- Trust scores: 1-hour cache

## Deployment Architecture

### Development

```
Docker Compose:
- postgres container
- redis container
- api container (FastAPI)
- worker container (Celery)
```

### Production (Future)

```
Cloud Provider: AWS/GCP

Services:
- ECS/EKS for containerized API
- RDS for PostgreSQL (Multi-AZ)
- ElastiCache for Redis
- ALB for load balancing
- S3 for file storage
- CloudWatch for monitoring
- CloudFront for CDN
```

### CI/CD Pipeline (Future)

```
GitHub Actions:
1. Run tests (pytest)
2. Lint code (black, flake8)
3. Build Docker image
4. Push to registry
5. Deploy to staging
6. Run integration tests
7. Deploy to production (manual approval)
```

## Monitoring & Observability

### Metrics (Future)

**Application Metrics**:
- Request rate and latency
- Error rates by endpoint
- User registration and login rates
- Job search queries per minute
- Vetting reports generated
- Cache hit ratios

**Business Metrics**:
- Active users (DAU, MAU)
- Subscription conversions
- Job applications submitted
- Scam reports filed
- Trust score distribution

### Logging

**Structured Logging**:
```python
logger.info("vetting_report_generated", extra={
    "user_id": user.id,
    "client_id": client.id,
    "trust_score": score,
    "duration_ms": duration
})
```

**Log Levels**:
- ERROR: Failures requiring attention
- WARNING: Degraded performance
- INFO: Important events (registrations, reports)
- DEBUG: Detailed troubleshooting (dev only)

### Alerts (Future)

**Critical Alerts**:
- Database connection failures
- API error rate > 5%
- Groq API failures
- Disk space > 90%

**Warning Alerts**:
- API latency > 2 seconds
- Cache miss rate > 50%
- Scraper failures

## Tech Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| API Framework | FastAPI | 0.109+ |
| Database | PostgreSQL | 15+ |
| ORM | SQLAlchemy | 2.0+ |
| Cache/Queue | Redis | 7.0+ |
| Task Queue | Celery | 5.3+ |
| AI Engine | Groq API | Latest |
| Auth | JWT + Bcrypt | - |
| Web Server | Uvicorn | 0.27+ |
| Frontend | React 18 | (Future) |
| CSS Framework | Tailwind CSS | (Future) |
| Deployment | Docker + Compose | Latest |

## Future Enhancements

1. **React Frontend**: Complete UI implementation
2. **Job Scrapers**: Implement all platform scrapers
3. **Real-time Alerts**: Celery + WebSockets
4. **Email Notifications**: SendGrid integration
5. **Payment Processing**: Stripe for subscriptions
6. **Mobile App**: React Native version
7. **Chrome Extension**: Instant vetting on platform sites
8. **AI Cover Letter Generator**: Use Groq to draft proposals
9. **Proposal Analyzer**: Review and improve user proposals
10. **Community Forum**: Freelancer discussions
11. **Time Tracking**: Integration with Toggl/Harvest
12. **Invoicing**: Generate invoices for completed work
13. **Tax Calculator**: Freelance tax estimation
14. **Contract Templates**: Legal contract generation
15. **Dispute Resolution**: Mediation tools

## Conclusion

This architecture provides a solid foundation for an AI-powered freelance platform. The modular design allows for easy extension and scaling. The integration with Groq's AI capabilities enables sophisticated client vetting and job matching features that differentiate this platform from traditional job boards.
