# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CarGPT is a unified car search & acquisition platform that aggregates vehicle listings from multiple sources. Currently, only eBay Motors API is fully functional due to anti-bot protections on other sources. The platform provides AI-powered features including natural language search, vehicle valuation analysis, personalized buyer questions, and communication assistance.

## Quick Start Commands

### Running the Application

```bash
# Primary method - uses bash script that handles port conflicts
./run_app.sh

# Alternative methods
python main.py                           # Direct Python execution
python start.py                          # Python launcher
python3 -m uvicorn main:app --reload --port 8601     # Direct uvicorn command
python debug_start.py                    # Debug mode on port 8080
```

### Testing

```bash
# Run comprehensive test suite (includes security tests)
python test_production_ready.py

# Run end-to-end UI tests with Playwright
python test_cujs_playwright.py

# Run data source connectivity tests
python test_framework.py

# Test specific components
python test_data_pipeline.py

# Test critical user journeys with Playwright (requires browser installation)
python test_cujs_playwright.py

# Test individual data sources (eBay, CarMax, etc.)
python test_sources_individually.py

# Docker testing (builds and tests container)
./docker-test.sh
```

### Docker Deployment

```bash
# Development deployment
docker-compose up --build

# Production deployment (includes PostgreSQL, Redis, Nginx, monitoring)
docker-compose -f docker-compose.prod.yml up --build

# Database initialization for production
docker exec -i findmycar-postgres psql -U cargpt cargpt_db < init-db.sql
```

## Architecture Overview

### Technology Stack
- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (dev), PostgreSQL (prod) with migration support
- **Frontend**: Server-side rendered HTML/JavaScript with Bootstrap 4
- **APIs**: eBay Browse API (fully functional), infrastructure for other sources
- **Caching**: Redis with cache manager for performance and rate limiting
- **Background Tasks**: Celery for async processing
- **Authentication**: JWT-based auth system (optional)
- **Monitoring**: Prometheus metrics, Grafana dashboards, health checks
- **Security**: Comprehensive input validation, CORS, rate limiting, security headers

### Core Components

1. **API Layer** (`main.py`)
   - FastAPI application with authentication middleware
   - Routes: `/`, `/search`, `/generate-message`, `/health`, `/monitoring`
   - Security headers and CORS configuration
   - Error handling with security considerations

2. **Data Source Integration**
   - `ebay_client.py` - eBay Browse API client (primary functional source)
   - `carmax_client.py`, `bat_client.py`, etc. - Infrastructure for future integrations
   - `cache_manager.py` - Centralized caching with TTL and rate limiting

3. **Search & Analysis**
   - `nlp_search.py` - Natural language query parsing
   - `valuation.py` - Vehicle pricing analysis with market comparisons
   - `ai_questions.py` - OpenAI-powered buyer question generation
   - `communication.py` - Message template generation

4. **Security & Validation**
   - `auth.py` - JWT authentication system
   - `config_validator.py` - Environment configuration validation
   - `validation_schemas.py` - Pydantic schemas for input validation
   - `error_handlers.py` - Security-aware error handling

5. **Database & Persistence**
   - `database.py` - SQLAlchemy models
   - `database_config.py` - Database configuration with connection pooling
   - `migrate_to_postgres.py` - SQLite to PostgreSQL migration utility
   - `init_db.py` - Database initialization

6. **Monitoring & Health**
   - `health_monitor.py` - Data source health monitoring
   - `logging_config.py` - Structured logging configuration
   - Integration with Prometheus/Grafana for production monitoring

## Configuration

### Environment Setup

```bash
# Copy example configuration
cp findmycar/.env.example findmycar/.env

# Edit with your API credentials
# Key files: .env, .env.prod.example, .env.test
```

### Required Environment Variables

```env
# Essential
EBAY_CLIENT_ID=your_ebay_client_id       # Required - eBay API access
EBAY_CLIENT_SECRET=your_ebay_secret      # Required - eBay API access
DATABASE_URL=sqlite:///./findmycar.db    # Database connection
SECRET_KEY=your-secret-key-here          # JWT authentication

# Optional but recommended
OPENAI_API_KEY=your_openai_key          # Enables AI features
REDIS_URL=redis://localhost:6379         # Caching and rate limiting
ALLOWED_ORIGINS=http://localhost:8601    # CORS configuration
LOG_LEVEL=INFO                           # Logging verbosity

# Chrome/Selenium Configuration (for web scraping)
CHROME_BIN=/usr/bin/google-chrome
CHROME_OPTIONS=--headless --no-sandbox --disable-dev-shm-usage --disable-gpu
```

### Database Operations

```bash
# Initialize database
python init_db.py

# Migrate from SQLite to PostgreSQL
python migrate_to_postgres.py

# Create cache tables (PostgreSQL)
python create_cache_tables.py

# Direct database access
sqlite3 findmycar.db                     # Development
psql -U cargpt cargpt_db                 # Production
```

## Development Workflow

### Adding New Features
1. API endpoints go in `main.py` with appropriate authentication decorators
2. Database models in `database.py` with corresponding Pydantic schemas
3. Business logic in dedicated modules
4. Input validation schemas in `validation_schemas.py`
5. Frontend templates in `templates/` with XSS protection
6. Update tests in relevant test files

### Security Considerations
- All user inputs are validated using Pydantic schemas
- SQL queries use parameterized statements via SQLAlchemy
- HTML outputs are escaped to prevent XSS
- Authentication is optional but fully implemented
- Rate limiting prevents abuse
- Sensitive configuration validated at startup

### Performance Optimization
- Redis caching with intelligent TTLs
- Database connection pooling
- Asynchronous request handling
- Background task processing with Celery
- CDN integration for static assets

## Production Deployment

The application includes enterprise-grade production infrastructure:

```bash
# Quick production setup
cp .env.prod.example .env.prod          # Configure with real values
docker-compose -f docker-compose.prod.yml up -d

# Production stack includes:
# - 2x FastAPI instances (load balanced)
# - PostgreSQL with connection pooling
# - Redis for caching and Celery broker
# - Nginx reverse proxy with SSL termination
# - Prometheus + Grafana monitoring
# - Automated health checks and restarts
```

### Monitoring Endpoints
- `/health` - Basic health check
- `/health/detailed` - Comprehensive system status
- `/monitoring` - Real-time monitoring dashboard
- `/metrics` - Prometheus metrics endpoint

## Data Source Status

**Current Reality:**
- ✅ eBay Motors API: Fully functional with rate limiting
- ❌ CarMax: Blocked by Cloudflare protection
- ❌ CarGurus: Blocked by anti-bot measures
- ❌ Bring a Trailer: Authentication required
- ❌ TrueCar: Geographic restrictions

The UI transparently shows which sources are available. Infrastructure exists for future integration when APIs become available or agreements are reached.

## Common Issues and Solutions

1. **Port conflicts**: Use `./run_app.sh` which handles port detection
2. **Missing API keys**: Check `.env` file configuration
3. **Database errors**: Run `python init_db.py` to initialize
4. **Cache issues**: Restart Redis or clear cache tables
5. **Test failures**: Ensure Playwright browsers are installed with `playwright install`
6. **Selenium/Chrome issues**: Install Chrome and ChromeDriver, or use `webdriver-manager`
7. **Module not found**: Ensure you're in the `findmycar/` directory when running commands

## Debugging Tips

```bash
# Debug specific data source
python debug_autotrader.py         # Test AutoTrader connectivity
python debug_cargurus.py           # Test CarGurus connectivity
python debug_ebay_quick.py         # Quick eBay API test

# Check data source health
python check_sources.py            # Verify all configured sources

# Enhanced search testing
python enhanced_demo.py            # Run the enhanced demo with advanced features
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/production-ready.yml`) includes:
- Security scanning with Bandit
- Dependency vulnerability checks
- Unit and integration tests
- Docker build verification
- Automated deployment hooks