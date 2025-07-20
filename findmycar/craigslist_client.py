"""
Craigslist Vehicle Listings Client
Accesses vehicle listings via RSS feeds for multiple regions
"""
import feedparser
import logging
from typing import List, Dict, Optional, Set
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class CraigslistClient:
    """
    Client for accessing Craigslist vehicle listings via RSS feeds
    """
    # Major US regions to search
    REGIONS = [
        'newyork', 'losangeles', 'chicago', 'houston', 'phoenix',
        'philadelphia', 'sanantonio', 'sandiego', 'dallas', 'austin',
        'jacksonville', 'indianapolis', 'sanfrancisco', 'columbus', 'fortworth',
        'charlotte', 'detroit', 'elpaso', 'seattle', 'denver',
        'washingtondc', 'boston', 'memphis', 'nashville', 'portland',
        'lasvegas', 'louisville', 'baltimore', 'milwaukee', 'albuquerque',
        'tucson', 'fresno', 'mesa', 'sacramento', 'atlanta',
        'kansascity', 'miami', 'raleigh', 'omaha', 'minneapolis'
    ]
    
    def __init__(self, regions: Optional[List[str]] = None):
        self.regions = regions or self.REGIONS[:10]  # Default to top 10 regions
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, page: int = 1,
                       per_page: int = 20) -> Dict:
        """
        Search Craigslist listings across multiple regions
        """
        try:
            logger.info(f"Searching Craigslist for: {query or 'all vehicles'}")
            
            # Build search query for RSS feeds
            search_params = self._build_search_params(query, make, model, 
                                                     year_min, year_max, 
                                                     price_min, price_max)
            
            # Search multiple regions in parallel
            all_vehicles = []
            seen_ids = set()  # Track unique listings
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_region = {
                    executor.submit(self._search_region, region, search_params): region
                    for region in self.regions
                }
                
                for future in as_completed(future_to_region):
                    region = future_to_region[future]
                    try:
                        vehicles = future.result()
                        # Deduplicate based on title and price
                        for vehicle in vehicles:
                            vehicle_key = f"{vehicle['title']}_{vehicle.get('price', 0)}"
                            if vehicle_key not in seen_ids:
                                seen_ids.add(vehicle_key)
                                all_vehicles.append(vehicle)
                    except Exception as e:
                        logger.error(f"Error searching region {region}: {str(e)}")
            
            # Sort by date (newest first)
            all_vehicles.sort(key=lambda x: x.get('created_date', ''), reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_vehicles = all_vehicles[start_idx:end_idx]
            
            return {
                'vehicles': paginated_vehicles,
                'total': len(all_vehicles),
                'page': page,
                'per_page': per_page,
                'source': 'craigslist'
            }
            
        except Exception as e:
            logger.error(f"Error searching Craigslist: {str(e)}")
            return self._empty_response()
    
    def _build_search_params(self, query: str, make: Optional[str], model: Optional[str],
                           year_min: Optional[int], year_max: Optional[int],
                           price_min: Optional[float], price_max: Optional[float]) -> Dict:
        """
        Build search parameters for Craigslist RSS
        """
        params = {}
        
        # Build query string
        query_parts = []
        if query:
            query_parts.append(query)
        if make:
            query_parts.append(make)
        if model:
            query_parts.append(model)
        
        if query_parts:
            params['query'] = ' '.join(query_parts)
        
        # Price range
        if price_min:
            params['min_price'] = int(price_min)
        if price_max:
            params['max_price'] = int(price_max)
        
        # Year range (Craigslist uses auto_year_min/max)
        if year_min:
            params['min_auto_year'] = year_min
        if year_max:
            params['max_auto_year'] = year_max
        
        return params
    
    def _search_region(self, region: str, params: Dict) -> List[Dict]:
        """
        Search a specific Craigslist region
        """
        try:
            # Build RSS URL
            base_url = f"https://{region}.craigslist.org/search/cta"
            rss_url = f"{base_url}?format=rss"
            
            # Add search parameters
            if params:
                from urllib.parse import urlencode
                param_str = urlencode(params)
                rss_url = f"{rss_url}&{param_str}"
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            vehicles = []
            for entry in feed.entries[:50]:  # Limit per region
                vehicle = self._parse_rss_entry(entry, region)
                if vehicle:
                    vehicles.append(vehicle)
            
            return vehicles
            
        except Exception as e:
            logger.error(f"Error searching Craigslist region {region}: {str(e)}")
            return []
    
    def _parse_rss_entry(self, entry: Dict, region: str) -> Optional[Dict]:
        """
        Parse RSS entry into vehicle dict
        """
        try:
            title = entry.get('title', '')
            description = entry.get('summary', '')
            link = entry.get('link', '')
            
            # Extract price from title (typically at the end like "$5000")
            price = None
            price_match = re.search(r'\$([0-9,]+)', title)
            if price_match:
                price = float(price_match.group(1).replace(',', ''))
                # Remove price from title
                title = title.replace(price_match.group(0), '').strip()
            
            # Extract year, make, model from title
            year = None
            year_match = re.search(r'\b(19|20)\d{2}\b', title)
            if year_match:
                year = int(year_match.group(0))
            
            # Parse make and model (heuristic approach)
            make = None
            model = None
            if year:
                # Remove year from title for easier parsing
                title_no_year = re.sub(r'\b(19|20)\d{2}\b', '', title).strip()
                parts = title_no_year.split()
                if parts:
                    # Common makes
                    common_makes = ['honda', 'toyota', 'ford', 'chevrolet', 'chevy', 
                                   'nissan', 'bmw', 'mercedes', 'audi', 'volkswagen',
                                   'mazda', 'subaru', 'hyundai', 'kia', 'jeep',
                                   'ram', 'gmc', 'buick', 'cadillac', 'lexus',
                                   'acura', 'infiniti', 'volvo', 'porsche', 'tesla']
                    
                    for i, part in enumerate(parts):
                        if part.lower() in common_makes:
                            make = part
                            if i + 1 < len(parts):
                                model = ' '.join(parts[i+1:])
                            break
                    
                    # If no common make found, assume first word is make
                    if not make and parts:
                        make = parts[0]
                        if len(parts) > 1:
                            model = ' '.join(parts[1:])
            
            # Extract location from region
            location = f"{region.replace('_', ' ').title()}, USA"
            
            # Get published date
            published = entry.get('published_parsed')
            if published:
                created_date = datetime(*published[:6]).isoformat()
            else:
                created_date = datetime.now().isoformat()
            
            # Extract image if available
            image = None
            if 'enclosures' in entry and entry['enclosures']:
                image = entry['enclosures'][0].get('href')
            
            return {
                'id': f"craigslist_{region}_{link.split('/')[-1].split('.')[0]}",
                'title': title or "Vehicle Listing",
                'price': price,
                'year': year,
                'make': make,
                'model': model,
                'mileage': None,  # Not in RSS feed
                'location': location,
                'link': link,
                'image': image,
                'description': description[:200] + '...' if len(description) > 200 else description,
                'source': 'craigslist',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': created_date,
                'region': region
            }
            
        except Exception as e:
            logger.error(f"Error parsing Craigslist RSS entry: {str(e)}")
            return None
    
    def _empty_response(self) -> Dict:
        """
        Return empty response structure
        """
        return {
            'vehicles': [],
            'total': 0,
            'page': 1,
            'per_page': 20,
            'source': 'craigslist'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        Since RSS doesn't provide all details, we'd need to scrape the actual listing
        """
        try:
            # For now, return None as scraping individual pages requires more care
            # Could be implemented later with proper rate limiting
            return None
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None
    
    def set_regions(self, regions: List[str]):
        """
        Set custom regions to search
        """
        self.regions = regions
    
    def get_available_regions(self) -> List[str]:
        """
        Get list of all available Craigslist regions
        """
        # This is a subset - full list has 400+ regions
        return [
            'atlanta', 'austin', 'boston', 'chicago', 'dallas', 'denver',
            'detroit', 'houston', 'lasvegas', 'losangeles', 'miami', 'minneapolis',
            'newyork', 'orlando', 'philadelphia', 'phoenix', 'portland', 'raleigh',
            'sacramento', 'sandiego', 'seattle', 'sfbay', 'tampa', 'washingtondc',
            # Add more regions as needed
        ]
    
    def check_health(self) -> Dict:
        """
        Check if Craigslist RSS feeds are accessible
        """
        try:
            # Test with a major region
            test_url = "https://newyork.craigslist.org/search/cta?format=rss"
            feed = feedparser.parse(test_url)
            is_healthy = len(feed.entries) > 0
            
            return {
                'source': 'craigslist',
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': 0.3,  # Approximate
                'message': f"Found {len(feed.entries)} listings in test region" if is_healthy else "No listings found"
            }
        except Exception as e:
            return {
                'source': 'craigslist',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }