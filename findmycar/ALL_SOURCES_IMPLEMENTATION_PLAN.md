# Implementation Plan for All 16 Vehicle Sources

## Sources Overview (From Autotempest)

### Currently Implemented ✅
1. **eBay Motors** - Working with official API
2. **CarMax** - Selenium scraper (limited)
3. **AutoTrader** - Selenium scraper (limited)

### To Be Implemented 🚧
1. **Carvana**
2. **Hemmings** 
3. **Cars & Bids**
4. **Cars.com**
5. **CarSoup.com**
6. **TrueCar**
7. **Autobytel**
8. **autoTRADER.ca** (Canadian)
9. **CarsDirect**
10. **Revy Autos**
11. **PrivateAuto**
12. **CarGurus**
13. **Craigslist**
14. **Autotrader** (Already partially implemented)
15. **Facebook Marketplace**

## Implementation Strategy by Source

### 1. Carvana 🟡
**Status**: API Research Needed
**Implementation**: 
```python
class CarvanaClient:
    """
    Carvana has a semi-public API used by their website
    """
    BASE_URL = "https://www.carvana.com/cars/api/v1/vehicles"
    
    def search(self, query, filters):
        # Their API accepts JSON POST requests
        # No official documentation but can reverse engineer
        pass
```

### 2. Hemmings 🟢
**Status**: RSS/XML Feeds Available
**Implementation**:
```python
class HemmingsClient:
    """
    Classic car marketplace with RSS feeds
    """
    RSS_URL = "https://www.hemmings.com/classifieds/rss"
    
    def get_listings(self):
        # Parse RSS/XML feeds
        # Focus on classic/vintage vehicles
        pass
```

### 3. Cars & Bids 🟢
**Status**: Public API-like endpoints
**Implementation**:
```python
class CarsBidsClient:
    """
    Auction site with accessible endpoints
    """
    BASE_URL = "https://carsandbids.com/api/v2/auctions"
    
    def get_active_auctions(self):
        # No auth required for public auctions
        # Returns JSON data
        pass
```

### 4. Cars.com 🟡
**Status**: Use Marketcheck API
**Implementation**:
```python
class CarsComClient:
    """
    Access via Marketcheck API (paid)
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://marketcheck-prod.apigee.net/v2"
    
    def search(self, query):
        # Marketcheck provides Cars.com inventory
        pass
```

### 5. CarSoup.com 🟢
**Status**: Simple HTML scraping
**Implementation**:
```python
class CarSoupClient:
    """
    Regional marketplace (Midwest US)
    """
    BASE_URL = "https://www.carsoup.com"
    
    def search(self, query):
        # Simple BeautifulSoup scraping
        # No advanced bot protection
        pass
```

### 6. TrueCar 🔴
**Status**: Heavy bot protection
**Implementation**:
```python
class TrueCarClient:
    """
    Requires advanced scraping techniques
    """
    def __init__(self):
        self.session = cloudscraper.create_scraper()
    
    def search(self, query):
        # Use cloudscraper for Cloudflare bypass
        pass
```

### 7. Autobytel 🟢
**Status**: Now part of AutoWeb, has dealer API
**Implementation**:
```python
class AutobytelClient:
    """
    B2B focused, dealer inventory
    """
    API_URL = "https://www.autoweb.com/api/inventory"
    
    def get_dealer_inventory(self, dealer_id):
        # Requires dealer partnership
        pass
```

### 8. autoTRADER.ca 🟡
**Status**: Canadian version, different from US
**Implementation**:
```python
class AutoTraderCAClient:
    """
    Canadian AutoTrader - different platform
    """
    BASE_URL = "https://www.autotrader.ca"
    
    def search(self, query, province=None):
        # Handles Canadian postal codes
        # Prices in CAD
        pass
```

### 9. CarsDirect 🟢
**Status**: Affiliate API available
**Implementation**:
```python
class CarsDirectClient:
    """
    Lead generation focused
    """
    def __init__(self, affiliate_id):
        self.affiliate_id = affiliate_id
        
    def get_listings(self):
        # Returns dealer inventory
        pass
```

### 10. Revy Autos 🟢
**Status**: Newer platform, simpler structure
**Implementation**:
```python
class RevyAutosClient:
    """
    Modern platform with JSON endpoints
    """
    API_URL = "https://www.revyautos.com/api/listings"
    
    def search(self, filters):
        # Clean JSON API
        pass
```

### 11. PrivateAuto 🟢
**Status**: Private party sales, API planned
**Implementation**:
```python
class PrivateAutoClient:
    """
    Private party marketplace
    """
    BASE_URL = "https://www.privateauto.com"
    
    def get_private_listings(self):
        # Focus on private sellers
        # Built-in escrow service
        pass
```

### 12. CarGurus 🔴
**Status**: Strong anti-bot (already attempted)
**Implementation**:
```python
class CarGurusClient:
    """
    Requires rotating proxies and headers
    """
    def __init__(self):
        self.proxies = self.load_proxy_pool()
        
    def search_with_proxy_rotation(self, query):
        # Implement proxy rotation
        # Use undetected-chromedriver
        pass
```

### 13. Craigslist 🟢
**Status**: RSS feeds available
**Implementation**:
```python
class CraigslistClient:
    """
    Use RSS feeds for each region
    """
    def get_region_feed(self, region):
        rss_url = f"https://{region}.craigslist.org/search/cta?format=rss"
        # Parse RSS feed
        pass
```

### 14. Facebook Marketplace 🔴
**Status**: No API, high risk
**Implementation**:
```python
class FacebookMarketplaceClient:
    """
    NOT RECOMMENDED - See separate document
    Consider user-submitted approach instead
    """
    pass
```

## Unified Source Manager

```python
class UnifiedSourceManager:
    """
    Manages all vehicle sources with fallback and caching
    """
    
    def __init__(self):
        self.sources = {
            'ebay': EbayClient(),
            'carvana': CarvanaClient(),
            'hemmings': HemmingsClient(),
            'cars_bids': CarsBidsClient(),
            'cars_com': CarsComClient(api_key=os.getenv('MARKETCHECK_KEY')),
            'carsoup': CarSoupClient(),
            'truecar': TrueCarClient(),
            'autobytel': AutobytelClient(),
            'autotrader_ca': AutoTraderCAClient(),
            'carsdirect': CarsDirectClient(affiliate_id=os.getenv('CARSDIRECT_ID')),
            'revy': RevyAutosClient(),
            'private_auto': PrivateAutoClient(),
            'cargurus': CarGurusClient(),
            'craigslist': CraigslistClient(),
            'autotrader': AutoTraderClient(),
            'carmax': CarMaxClient()
        }
        
        self.source_config = {
            'ebay': {'enabled': True, 'priority': 1, 'type': 'api'},
            'carvana': {'enabled': True, 'priority': 2, 'type': 'scrape'},
            'hemmings': {'enabled': True, 'priority': 3, 'type': 'rss'},
            'cars_bids': {'enabled': True, 'priority': 4, 'type': 'api'},
            'craigslist': {'enabled': True, 'priority': 5, 'type': 'rss'},
            # ... configure each source
        }
    
    async def search_all_sources(self, query, filters):
        """
        Search all enabled sources in parallel
        """
        enabled_sources = [
            name for name, config in self.source_config.items() 
            if config['enabled']
        ]
        
        # Sort by priority
        enabled_sources.sort(
            key=lambda x: self.source_config[x]['priority']
        )
        
        # Search in parallel with timeout
        results = await asyncio.gather(*[
            self.search_source_with_timeout(source, query, filters)
            for source in enabled_sources
        ])
        
        return self.merge_and_dedupe_results(results)
```

## Implementation Phases

### Phase 1: Easy Wins (Week 1)
- [ ] Hemmings (RSS feeds)
- [ ] Cars & Bids (Public API)
- [ ] Craigslist (RSS feeds)
- [ ] CarSoup (Simple scraping)
- [ ] Revy Autos (JSON endpoints)

### Phase 2: API Integrations (Week 2) ✅
- [x] Carvana (Semi-public API)
- [x] Cars.com via Marketcheck
- [x] CarsDirect (Affiliate API)
- [x] Autobytel/AutoWeb
- [ ] PrivateAuto

### Phase 3: Advanced Scraping (Week 3-4)
- [ ] Carvana (Reverse engineer API)
- [ ] autoTRADER.ca
- [ ] TrueCar (Cloudscraper)
- [ ] CarGurus (Proxy rotation)

### Phase 4: Special Cases (Week 5)
- [ ] Facebook Marketplace (User submissions only)
- [ ] Enhance existing AutoTrader/CarMax

## Technical Requirements

### 1. Infrastructure
```yaml
# docker-compose.yml additions
services:
  proxy-pool:
    image: scrapoxy/proxy
    environment:
      - PROVIDERS=brightdata,smartproxy
  
  selenium-grid:
    image: selenium/hub:4.15.0
    environment:
      - GRID_MAX_SESSION=10
```

### 2. Dependencies
```python
# requirements.txt additions
marketcheck==2.0.0          # Cars.com API
cloudscraper==1.2.71        # Cloudflare bypass
scrapy==2.11.0              # Advanced scraping
scrapy-splash==0.9.0        # JavaScript rendering
feedparser==6.0.10          # RSS parsing
python-craigslist==1.0.3    # Craigslist helper
```

### 3. Caching Strategy
```python
CACHE_TTL = {
    'api': 3600,        # 1 hour for API results
    'scrape': 7200,     # 2 hours for scraped data
    'rss': 1800,        # 30 min for RSS feeds
    'auction': 300      # 5 min for auction sites
}
```

## Legal Compliance Matrix

| Source | API Available | Scraping Allowed | Terms Risk | Implementation |
|--------|--------------|------------------|------------|----------------|
| eBay | ✅ Official | ✅ | Low | API |
| Carvana | ❌ | ⚠️ | Medium | Careful scraping |
| Hemmings | ✅ RSS | ✅ | Low | RSS |
| Cars & Bids | ✅ Unofficial | ✅ | Low | API |
| Cars.com | ✅ Via 3rd party | ❌ | Low | Marketcheck |
| Facebook | ❌ | ❌ | High | User submissions |
| Craigslist | ✅ RSS | ✅ | Low | RSS |
| CarGurus | ❌ | ❌ | High | Advanced scraping |

## Monitoring & Health Checks

```python
class SourceHealthMonitor:
    """
    Monitor all sources for availability
    """
    
    def check_all_sources(self):
        health_status = {}
        
        for source_name, client in self.sources.items():
            try:
                # Test with simple query
                result = client.search("honda civic", limit=1)
                health_status[source_name] = {
                    'status': 'healthy',
                    'response_time': result.get('response_time'),
                    'result_count': len(result.get('vehicles', []))
                }
            except Exception as e:
                health_status[source_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        return health_status
```

## Next Steps

1. **Prioritize by value**: Focus on sources with most inventory
2. **Start with low-risk**: RSS feeds and public APIs first
3. **Build incrementally**: Add sources one at a time
4. **Monitor performance**: Track success rates
5. **Stay compliant**: Always respect robots.txt and ToS