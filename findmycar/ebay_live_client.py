#!/usr/bin/env python3
"""
Production-ready eBay Motors API client with caching and rate limiting
"""

import os
import base64
import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import json
from functools import lru_cache
import redis
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class EbayLiveClient:
    """Production eBay Browse API client with caching and rate limiting"""
    
    def __init__(self):
        self.client_id = os.environ.get('EBAY_CLIENT_ID')
        self.client_secret = os.environ.get('EBAY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("EBAY_CLIENT_ID and EBAY_CLIENT_SECRET must be set")
        
        # Initialize Redis for caching (optional)
        self.redis_client = None
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis caching enabled")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 10 requests per second max
        
        # Token cache
        self._token = None
        self._token_expires = None
        
        # API endpoints
        self.auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
        self.search_url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        self.item_url = "https://api.ebay.com/buy/browse/v1/item"
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_oauth_token(self) -> str:
        """Get OAuth token with caching and retry logic"""
        # Check if we have a valid cached token
        if self._token and self._token_expires and datetime.now() < self._token_expires:
            return self._token
        
        # Create base64 encoded credentials
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {credentials}'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        self._rate_limit()
        response = requests.post(self.auth_url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        self._token = token_data['access_token']
        # Token typically expires in 2 hours, refresh 5 minutes early
        expires_in = token_data.get('expires_in', 7200)
        self._token_expires = datetime.now() + timedelta(seconds=expires_in - 300)
        
        logger.info("Successfully obtained eBay OAuth token")
        return self._token
    
    def _get_cache_key(self, query: str, filters: Dict[str, Any], page: int = 1) -> str:
        """Generate cache key for search results"""
        # Create a deterministic key from search parameters
        key_parts = [
            f"ebay:search:v1",
            f"q:{query}",
            f"p:{page}"
        ]
        
        # Add sorted filters to ensure consistency
        for k, v in sorted(filters.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        
        return ":".join(key_parts)
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache"""
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache get error: {e}")
        return None
    
    def _set_cache(self, cache_key: str, data: Dict, ttl: int = 300):
        """Set data in cache with TTL (default 5 minutes)"""
        if self.redis_client:
            try:
                self.redis_client.setex(cache_key, ttl, json.dumps(data))
            except Exception as e:
                logger.warning(f"Cache set error: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def search_vehicles(self, 
                       query: str = "",
                       make: Optional[str] = None,
                       model: Optional[str] = None,
                       year_min: Optional[int] = None,
                       year_max: Optional[int] = None,
                       price_min: Optional[float] = None,
                       price_max: Optional[float] = None,
                       mileage_max: Optional[int] = None,
                       page: int = 1,
                       per_page: int = 20,
                       use_cache: bool = True) -> Dict[str, Any]:
        """
        Search for vehicles on eBay Motors with advanced filtering
        """
        # Build search query
        search_terms = []
        if query:
            search_terms.append(query)
        if make:
            search_terms.append(make)
        if model:
            search_terms.append(model)
        
        search_query = " ".join(search_terms) if search_terms else "cars"
        
        # Build filters
        filters = {
            'make': make,
            'model': model,
            'year_min': year_min,
            'year_max': year_max,
            'price_min': price_min,
            'price_max': price_max,
            'mileage_max': mileage_max
        }
        
        # Check cache first
        cache_key = self._get_cache_key(search_query, filters, page)
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"Returning cached results for: {cache_key}")
                return cached_result
        
        # Get OAuth token
        token = self._get_oauth_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        # Build API filters
        api_filters = []
        
        # Price filter
        if price_min or price_max:
            min_price = price_min or 0
            max_price = price_max or 999999
            api_filters.append(f"price:[{min_price}..{max_price}]")
        
        # Only include fixed price listings (no auctions)
        api_filters.append("buyingOptions:{FIXED_PRICE}")
        
        # Location filter - US only
        api_filters.append("itemLocationCountry:US")
        
        # Build parameters
        params = {
            'q': search_query,
            'category_ids': '6001',  # Cars & Trucks
            'limit': per_page,
            'offset': (page - 1) * per_page,
            'sort': 'price',
            'filter': ','.join(api_filters) if api_filters else None
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        # Make API request
        self._rate_limit()
        response = requests.get(self.search_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Process results
        vehicles = []
        for item in data.get('itemSummaries', []):
            vehicle = self._parse_vehicle(item)
            
            # Apply additional filters that eBay API doesn't support
            if year_min and vehicle.get('year') and vehicle['year'] < year_min:
                continue
            if year_max and vehicle.get('year') and vehicle['year'] > year_max:
                continue
            if mileage_max and vehicle.get('mileage') and vehicle['mileage'] > mileage_max:
                continue
            
            vehicles.append(vehicle)
        
        result = {
            'vehicles': vehicles,
            'total': data.get('total', 0),
            'page': page,
            'per_page': per_page,
            'pages': (data.get('total', 0) + per_page - 1) // per_page,
            'cached': False,
            'search_time': datetime.utcnow().isoformat()
        }
        
        # Cache the result
        self._set_cache(cache_key, result)
        
        return result
    
    def _parse_vehicle(self, item: Dict) -> Dict:
        """Parse eBay item into standardized vehicle format"""
        # Extract year, make, model from title
        title = item.get('title', '')
        year, make, model = self._extract_vehicle_info(title)
        
        # Extract mileage from subtitle or condition
        mileage = self._extract_mileage(item.get('subtitle', '') + ' ' + item.get('condition', ''))
        
        # Get location
        location = item.get('itemLocation', {})
        location_str = f"{location.get('city', '')}, {location.get('stateOrProvince', '')}"
        
        # Get images
        image_urls = []
        if 'thumbnailImages' in item:
            for img in item['thumbnailImages']:
                image_urls.append(img.get('imageUrl', ''))
        elif 'image' in item:
            image_urls.append(item['image'].get('imageUrl', ''))
        
        # Get price
        price = None
        if 'price' in item:
            price = float(item['price'].get('value', 0))
        
        return {
            'listing_id': item.get('itemId'),
            'source': 'ebay',
            'title': title,
            'year': year,
            'make': make,
            'model': model,
            'price': price,
            'mileage': mileage,
            'location': location_str.strip(', '),
            'view_item_url': item.get('itemWebUrl'),
            'image_urls': image_urls,
            'condition': item.get('condition'),
            'seller': item.get('seller', {}).get('username'),
            'listing_end': item.get('itemEndDate'),
            'body_style': self._guess_body_style(title, model),
            'created_at': datetime.utcnow().isoformat()
        }
    
    def _extract_vehicle_info(self, title: str) -> tuple:
        """Extract year, make, and model from title"""
        import re
        
        # Common patterns
        year_pattern = r'\b(19\d{2}|20\d{2})\b'
        
        # Extract year
        year_match = re.search(year_pattern, title)
        year = int(year_match.group(1)) if year_match else None
        
        # Remove year from title for easier parsing
        title_no_year = re.sub(year_pattern, '', title) if year else title
        
        # Known makes
        makes = ['Honda', 'Toyota', 'Ford', 'Chevrolet', 'GMC', 'Nissan', 'Mazda', 
                'Hyundai', 'Kia', 'Subaru', 'Volkswagen', 'BMW', 'Mercedes-Benz',
                'Audi', 'Lexus', 'Acura', 'Infiniti', 'Cadillac', 'Buick', 'Lincoln',
                'Dodge', 'Ram', 'Jeep', 'Chrysler', 'Tesla', 'Volvo', 'Porsche']
        
        make = None
        model = None
        
        # Find make
        for m in makes:
            if m.lower() in title.lower():
                make = m
                # Extract model (words after make)
                pattern = rf'{m}\s+(\w+(?:\s+\w+)?)'
                model_match = re.search(pattern, title, re.IGNORECASE)
                if model_match:
                    model = model_match.group(1).strip()
                break
        
        return year, make, model
    
    def _extract_mileage(self, text: str) -> Optional[int]:
        """Extract mileage from text"""
        import re
        
        # Look for patterns like "50,000 miles" or "50k miles"
        patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:miles|mi\.?)',
            r'(\d+)k\s*(?:miles|mi\.?)',
            r'mileage[:\s]+(\d{1,3}(?:,\d{3})*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                mileage_str = match.group(1)
                if 'k' in text[match.start():match.end()]:
                    return int(mileage_str) * 1000
                else:
                    return int(mileage_str.replace(',', ''))
        
        return None
    
    def _guess_body_style(self, title: str, model: str) -> Optional[str]:
        """Guess body style from title and model"""
        text = (title + ' ' + (model or '')).lower()
        
        body_styles = {
            'suv': ['suv', 'sport utility'],
            'truck': ['truck', 'pickup', 'f-150', 'f-250', 'silverado', 'ram', 'tacoma', 'tundra'],
            'sedan': ['sedan', 'accord', 'camry', 'civic', 'corolla', 'altima'],
            'coupe': ['coupe', 'mustang', 'camaro', 'challenger'],
            'convertible': ['convertible', 'cabriolet', 'roadster'],
            'wagon': ['wagon', 'estate'],
            'van': ['van', 'minivan'],
            'hatchback': ['hatchback', 'hatch']
        }
        
        for style, keywords in body_styles.items():
            if any(keyword in text for keyword in keywords):
                return style
        
        return None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_vehicle_details(self, item_id: str, use_cache: bool = True) -> Optional[Dict]:
        """Get detailed information about a specific vehicle"""
        cache_key = f"ebay:item:v1:{item_id}"
        
        # Check cache
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
        
        token = self._get_oauth_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        url = f"{self.item_url}/{item_id}"
        
        self._rate_limit()
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        
        item = response.json()
        vehicle = self._parse_vehicle_detailed(item)
        
        # Cache for longer (1 hour) since details change less frequently
        self._set_cache(cache_key, vehicle, ttl=3600)
        
        return vehicle
    
    def _parse_vehicle_detailed(self, item: Dict) -> Dict:
        """Parse detailed eBay item data"""
        # Start with basic parsing
        vehicle = self._parse_vehicle(item)
        
        # Add detailed information
        vehicle['description'] = item.get('shortDescription', '')
        
        # Extract attributes from item specifics
        attributes = {}
        features = []
        
        for specific in item.get('localizedAspects', []):
            name = specific.get('name', '').lower()
            value = specific.get('value')
            
            if not value:
                continue
            
            # Map to standardized attributes
            if 'vin' in name:
                vehicle['vin'] = value
            elif 'transmission' in name:
                vehicle['transmission'] = value
            elif 'fuel type' in name:
                vehicle['fuel_type'] = value
            elif 'drivetrain' in name or 'drive type' in name:
                vehicle['drivetrain'] = value
            elif 'engine' in name and 'size' in name:
                attributes['engine_size'] = value
            elif 'mpg' in name:
                if 'city' in name:
                    attributes['mpg_city'] = self._extract_number(value)
                elif 'highway' in name:
                    attributes['mpg_highway'] = self._extract_number(value)
            elif 'doors' in name:
                attributes['doors'] = self._extract_number(value)
            elif 'color' in name:
                if 'exterior' in name:
                    vehicle['exterior_color'] = value
                elif 'interior' in name:
                    vehicle['interior_color'] = value
            else:
                # Store as feature if it looks like one
                if any(keyword in name for keyword in ['leather', 'navigation', 'sunroof', 'camera', 'heated']):
                    features.append(value)
        
        vehicle['attributes'] = attributes
        vehicle['features'] = features
        
        return vehicle
    
    def _extract_number(self, text: str) -> Optional[float]:
        """Extract number from text"""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', str(text))
        return float(match.group(1)) if match else None