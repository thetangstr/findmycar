# AutoNavigator Data Architecture Proposal

## Current Issues

### Cars.com Integration Problems
1. **Fake Data**: Currently generating realistic but fake vehicle data
2. **Search Links**: URLs redirect to search results, not individual listings
3. **No Real Inventory**: No connection to actual Cars.com listings

### Data Storage Inefficiencies  
1. **Static Storage**: Storing all vehicle data permanently in SQLite
2. **Stale Data**: No data freshness guarantees
3. **Storage Bloat**: Database grows without cleanup
4. **No Caching Strategy**: No differentiation between frequently/rarely accessed data

## Proposed Architecture

### 1. Hybrid Data Strategy

#### Primary Data Sources (Live API)
- **eBay Motors API**: Real-time data via official API ✅
- **Automotive Data Providers**: Consider services like:
  - AutoTrader API
  - Cars.com Partner API (if available)
  - CarGurus API
  - Edmunds API

#### Data Flow Design
```
User Search → Check Cache → API Call (if needed) → Cache Results → Display
```

### 2. Intelligent Caching System

#### Cache Levels
1. **Hot Cache** (Redis/Memory): Frequently searched queries (1-24 hours)
2. **Warm Cache** (Database): Popular searches (1-7 days)  
3. **Cold Storage** (Archive): Historical data for analytics

#### Cache Strategy
```python
# Example caching logic
def search_vehicles(query, filters):
    cache_key = generate_cache_key(query, filters)
    
    # Check hot cache first (Redis)
    if results := hot_cache.get(cache_key):
        return results
    
    # Check warm cache (Database)
    if results := warm_cache.get(cache_key, max_age=24h):
        hot_cache.set(cache_key, results, ttl=1h)
        return results
    
    # Make live API calls
    results = fetch_live_data(query, filters)
    
    # Cache results based on query popularity
    if is_popular_query(query):
        warm_cache.set(cache_key, results, ttl=24h)
    hot_cache.set(cache_key, results, ttl=1h)
    
    return results
```

### 3. Database Schema Redesign

#### Core Tables
```sql
-- Cached search results with expiration
CREATE TABLE search_cache (
    id INTEGER PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE,
    query_hash VARCHAR(64),
    results JSON,
    source VARCHAR(50),
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 1,
    last_accessed TIMESTAMP
);

-- Popular queries for caching decisions
CREATE TABLE query_analytics (
    id INTEGER PRIMARY KEY,
    query_normalized VARCHAR(255),
    search_count INTEGER DEFAULT 1,
    last_searched TIMESTAMP,
    avg_results INTEGER
);

-- Minimal vehicle storage for favorites/history
CREATE TABLE vehicle_references (
    id INTEGER PRIMARY KEY,
    external_id VARCHAR(255),
    source VARCHAR(50),
    title VARCHAR(500),
    price DECIMAL(10,2),
    cached_data JSON,
    created_at TIMESTAMP
);
```

### 4. Cars.com Solution Options

#### Option A: Third-Party Automotive APIs
- **AutoTrader API**: Professional automotive data
- **CarGurus API**: Comprehensive vehicle listings
- **Automotive Data Exchange**: Industry-standard data feeds

#### Option B: Cars.com Partnership/API
- Research Cars.com's official partner program
- Business development approach for API access

#### Option C: Enhanced eBay Focus
- Make eBay the primary, authoritative source
- Use Cars.com as price comparison/validation
- Clear labeling of data sources

### 5. Implementation Plan

#### Phase 1: Core Caching (Week 1)
1. Implement Redis caching layer
2. Add cache key generation
3. Update eBay integration to use caching
4. Add cache analytics

#### Phase 2: Data Source Research (Week 2)
1. Evaluate automotive data providers
2. Test API integrations
3. Compare data quality and coverage
4. Cost analysis

#### Phase 3: Production Architecture (Week 3-4)
1. Implement chosen data sources
2. Deploy caching system
3. Add data expiration and cleanup
4. Performance monitoring

### 6. Technology Stack

#### Caching Layer
- **Redis**: Hot cache (in-memory, fast)
- **PostgreSQL**: Warm cache (structured, queryable)
- **Background Jobs**: Cache refresh and cleanup

#### Data Sources
- **eBay Browse API**: Primary automotive source
- **TBD Automotive API**: Secondary source for Cars.com-style data
- **Fallback System**: Graceful degradation when APIs unavailable

### 7. Benefits

#### Performance
- **Fast Response**: Cached results serve in <100ms
- **Reduced API Costs**: Fewer external API calls
- **Better UX**: Consistent, fast search experience

#### Data Quality
- **Real Data**: No more fake/sample data
- **Fresh Data**: Automatic cache expiration
- **Multiple Sources**: Data validation and comparison

#### Scalability
- **Storage Efficiency**: Only cache popular searches
- **Cost Control**: Intelligent API usage
- **Growth Ready**: Architecture scales with users

## Immediate Next Steps

1. **Quick Fix**: Temporarily disable Cars.com or clearly label as "Reference Data"
2. **Research Phase**: Evaluate automotive data providers
3. **Pilot Implementation**: Test caching with eBay data
4. **Production Rollout**: Implement full architecture

## Cost Considerations

- **Redis Hosting**: ~$10-50/month (managed service)
- **Automotive APIs**: $0.01-0.10 per search (varies by provider)
- **Storage**: Minimal increase with intelligent caching
- **Development**: 2-3 weeks initial implementation