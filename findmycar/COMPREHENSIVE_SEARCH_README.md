# Comprehensive Vehicle Search System

This document describes the new comprehensive search system with advanced filtering capabilities.

## Features

### 1. Multi-Layer Search
- **Natural Language Processing**: Parse queries like "red SUV under 30k with leather seats"
- **Structured Filters**: Filter by make, model, year, price, mileage, body style, colors, etc.
- **JSONB Attributes**: Filter by MPG, seating capacity, horsepower, electric range
- **Feature Search**: Find vehicles with specific features (backup camera, sunroof, etc.)
- **Full-Text Search**: Search across title, description, and all text fields

### 2. Smart Presets
Pre-configured searches for common use cases:
- **Family SUV**: 7+ seats, backup camera, safety features
- **Fuel Efficient**: 30+ MPG or hybrid/electric
- **Luxury**: Premium brands with luxury features
- **First Car**: Under $15k, recent year, low mileage
- **Off-Road**: 4WD/AWD trucks and SUVs
- **Sports Car**: High performance coupes and convertibles
- **Electric**: All-electric vehicles
- **Work Truck**: Pickup trucks with towing capability

### 3. Advanced Filters

#### Body & Style
- Body style selector with visual icons
- Exterior color palette with multi-select
- Color exclusion (e.g., "not white")
- Interior color filtering

#### Mechanical & Performance
- Transmission type (automatic, manual, CVT, dual-clutch)
- Drivetrain (FWD, RWD, AWD, 4WD)
- Fuel type (gas, hybrid, plug-in hybrid, electric, diesel)
- Engine size and cylinders
- Horsepower minimum

#### Features & Technology
- Safety features (backup camera, blind spot monitoring, etc.)
- Comfort features (leather seats, heated/cooled seats, sunroof)
- Technology (Apple CarPlay, Android Auto, navigation)
- Convenience (keyless entry, remote start, third row)

#### Efficiency
- Minimum city MPG
- Minimum highway MPG
- Minimum combined MPG
- Electric range for EVs

#### History & Condition
- Clean title only
- No accidents reported
- One owner vehicles
- Certified pre-owned

### 4. Saved Searches
- Save any search configuration with a custom name
- Run saved searches with one click
- Track when searches were last run
- Get notifications for new matches (future feature)

### 5. Search Suggestions
- Auto-complete for makes and models
- Suggest relevant search presets
- Show popular searches

## Setup Instructions

### 1. Install PostgreSQL
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
createdb findmycar
```

### 2. Set Environment Variables
```bash
# Add to .env file
DATABASE_URL=postgresql://localhost/findmycar
REDIS_URL=redis://localhost:6379  # Optional, for caching
```

### 3. Run Migration
```bash
# Test the system first
python test_comprehensive_search.py

# If using existing SQLite data, migrate it
python migrate_to_v2.py

# Or start fresh
python init_db.py  # Uses database_v2.py schema
```

### 4. Start the Application
```bash
# Run the enhanced Flask app
python flask_app_v2.py

# Access at http://localhost:8602
```

## API Endpoints

### Search Vehicles
```
GET/POST /api/search/v2
```

Parameters:
- `query`: Natural language search query
- `preset`: Smart preset ID (e.g., 'family_suv', 'fuel_efficient')
- `make`: Comma-separated makes
- `model`: Model name
- `year_min`, `year_max`: Year range
- `price_min`, `price_max`: Price range
- `mileage_min`, `mileage_max`: Mileage range
- `body_style`: Comma-separated body styles
- `exterior_color`: Comma-separated colors to include
- `exclude_colors`: Comma-separated colors to exclude
- `transmission`: Comma-separated transmission types
- `drivetrain`: Comma-separated drivetrain types
- `fuel_type`: Comma-separated fuel types
- `required_features`: Comma-separated feature requirements
- `mpg_city_min`: Minimum city MPG
- `mpg_highway_min`: Minimum highway MPG
- `clean_title_only`: Boolean
- `no_accidents`: Boolean
- `one_owner_only`: Boolean
- `certified_only`: Boolean
- `sort_by`: Sort order (relevance, price_low, price_high, mileage_low, year_new, recent)
- `page`: Page number
- `per_page`: Results per page

### Get Search Suggestions
```
GET /api/search/suggestions?q=query
```

### Saved Searches
```
GET /api/saved-searches?user_id=xxx
POST /api/saved-searches/{id}/run
```

### Vehicle Details
```
GET /api/vehicle/{id}
```

## Database Schema

The new schema uses PostgreSQL with JSONB for flexibility:

```sql
CREATE TABLE vehicles_v2 (
    -- Core indexed fields for fast filtering
    id SERIAL PRIMARY KEY,
    listing_id VARCHAR UNIQUE,
    source VARCHAR,
    make VARCHAR,
    model VARCHAR,
    year INTEGER,
    price FLOAT,
    mileage INTEGER,
    body_style VARCHAR,
    exterior_color VARCHAR,
    interior_color VARCHAR,
    transmission VARCHAR,
    drivetrain VARCHAR,
    fuel_type VARCHAR,
    
    -- Location
    location VARCHAR,
    zip_code VARCHAR,
    
    -- Content
    title VARCHAR,
    description TEXT,
    image_urls JSONB,  -- Array of image URLs
    
    -- Flexible attributes (JSONB)
    attributes JSONB,  -- MPG, horsepower, dimensions, etc.
    features JSONB,    -- Array of feature names
    history JSONB,     -- Ownership, accidents, service
    pricing_analysis JSONB,
    
    -- Full-text search
    search_vector TSVECTOR,
    
    -- Metadata
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for performance
CREATE INDEX idx_make_model ON vehicles_v2(make, model);
CREATE INDEX idx_year_price ON vehicles_v2(year, price);
CREATE INDEX idx_attributes_gin ON vehicles_v2 USING GIN(attributes);
CREATE INDEX idx_features_gin ON vehicles_v2 USING GIN(features);
CREATE INDEX idx_search_vector ON vehicles_v2 USING GIN(search_vector);
```

## Architecture

### Components
1. **database_v2.py**: PostgreSQL schema with JSONB support
2. **attribute_standardizer.py**: Normalizes data from different sources
3. **comprehensive_search_engine.py**: Multi-layer search implementation
4. **ebay_enhanced_extractor.py**: Enhanced data extraction from eBay
5. **flask_app_v2.py**: API endpoints for comprehensive search
6. **comprehensive_search.html**: Advanced filter UI

### Data Flow
1. Raw data from sources (eBay, CarMax, etc.)
2. Enhanced extraction pulls all available attributes
3. Attribute standardizer normalizes to consistent format
4. Data stored in PostgreSQL with JSONB for flexibility
5. Search engine applies multiple filter layers
6. Results ranked by relevance and user preferences

## Future Enhancements

1. **Real-time notifications**: Alert users when new matches appear
2. **Price tracking**: Track price changes over time
3. **Comparison tool**: Compare multiple vehicles side-by-side
4. **Market insights**: Show pricing trends and market analysis
5. **Dealer integration**: Direct communication with sellers
6. **Mobile app**: Native mobile experience
7. **AI recommendations**: Personalized vehicle suggestions