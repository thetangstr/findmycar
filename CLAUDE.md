# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AutoNavigator is a unified car search & acquisition platform that aggregates vehicle listings from eBay Motors. It provides AI-powered features including natural language search, vehicle valuation analysis, personalized buyer questions, and communication assistance.

## Quick Start Commands

### Running the Application

```bash
# Primary method - uses bash script that handles port conflicts
./run_app.sh

# Alternative methods
python start.py                           # Python launcher
python3 -m uvicorn main:app --reload     # Direct uvicorn command
python debug_start.py                     # Debug mode on port 8080
```

### Installation

```bash
pip install -r requirements.txt
```

## Configuration

The application requires environment variables in `.env` file:

```env
EBAY_CLIENT_ID=your_ebay_client_id       # Required - eBay API access
EBAY_CLIENT_SECRET=your_ebay_secret      # Required - eBay API access
OPENAI_API_KEY=your_openai_key          # Optional - enables AI features
DATABASE_URL=sqlite:///./findmycar.db    # Default SQLite database
```

Note: The existing `.env` file already contains eBay API credentials.

## Architecture Overview

### Technology Stack
- **Backend**: FastAPI (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML/JavaScript with Bootstrap 4
- **APIs**: eBay Browse API, OpenAI API

### Core Components

1. **API Layer** (`main.py`)
   - FastAPI application with routes:
     - `/` - Main web interface
     - `/ingest` - Data ingestion endpoint
     - `/generate-message` - Communication template generation

2. **eBay Integration** (`ebay_client.py`)
   - Browse API client for searching eBay Motors
   - Handles API authentication and pagination
   - Extracts vehicle details and specifications

3. **Search Processing** (`nlp_search.py`)
   - Natural language query parsing
   - Converts user queries to eBay API parameters
   - Supports queries like "Tesla under $50k" or "2019-2021 Honda Civic"

4. **Valuation Engine** (`valuation.py`)
   - Analyzes vehicle pricing relative to market
   - Generates deal ratings (Excellent/Good/Fair/Overpriced)
   - Considers mileage, year, and market comparisons

5. **AI Features** (`ai_questions.py`)
   - Generates personalized buyer questions using OpenAI
   - Creates relevant inquiries based on vehicle specifics

6. **Communication** (`communication.py`)
   - Generates message templates for:
     - Initial seller inquiries
     - Negotiation messages
     - Follow-up communications

### Database Schema

The `Vehicle` model includes:
- Basic info: title, price, location, URLs
- Specifications: make, model, year, mileage, condition
- Valuation data: estimated value, deal rating
- AI-generated content: buyer questions
- Metadata: timestamps, seller info

## Development Workflow

1. **Adding New Features**
   - API endpoints go in `main.py`
   - Database models in `database.py`
   - Business logic in dedicated modules

2. **Testing Changes**
   - Run with `--reload` flag for hot reloading
   - Access web interface at `http://localhost:8000`
   - API documentation at `http://localhost:8000/docs`

3. **Database Operations**
   - CRUD operations in `crud.py`
   - SQLite database file: `findmycar.db`
   - Models defined in `database.py`

## Key Dependencies

- **fastapi==0.111.0** - Web framework
- **sqlalchemy==2.0.30** - Database ORM
- **ebaysdk==2.2.0** - eBay API integration
- **openai==0.28.1** - AI features
- **uvicorn==0.30.1** - ASGI server
- **pydantic==2.7.2** - Data validation
- **python-dotenv==1.0.1** - Environment configuration