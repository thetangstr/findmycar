"""
Unified Source Manager for All Vehicle Sources
Manages 16+ vehicle data sources with fallback and caching
"""
import os
import logging
import asyncio
from typing import List, Dict, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import traceback

# Import all source clients
from ebay_live_client import EbayLiveClient
from carmax_wrapper import CarMaxWrapper
from autotrader_wrapper import AutoTraderWrapper
from hemmings_client import HemmingsClient
from cars_bids_client import CarsBidsClient
from facebook_marketplace_client import FacebookMarketplaceClient
from craigslist_client import CraigslistClient
from carsoup_client import CarSoupClient
from revy_autos_client import RevyAutosClient
from cargurus_client import CarGurusClient
from truecar_client import TrueCarClient

# Phase 2 imports
from carvana_client import CarvanaClient
from cars_com_client import CarsComClient
from autobytel_client import AutobytelClient
from carsdirect_client import CarsDirectClient
# from autotrader_ca_client import AutoTraderCAClient
# from private_auto_client import PrivateAutoClient

logger = logging.getLogger(__name__)

class UnifiedSourceManager:
    """
    Manages all vehicle sources with intelligent fallback and caching
    """
    
    def __init__(self, cache_manager=None):
        self.cache_manager = cache_manager
        
        # Initialize all available sources
        self.sources = self._initialize_sources()
        
        # Source configuration with metadata
        self.source_config = {
            'ebay': {
                'enabled': True,
                'priority': 1,
                'type': 'api',
                'timeout': 10,
                'description': 'eBay Motors - Largest online vehicle marketplace'
            },
            'hemmings': {
                'enabled': True,
                'priority': 2,
                'type': 'rss',
                'timeout': 5,
                'description': 'Hemmings - Classic and collector cars'
            },
            'cars_bids': {
                'enabled': True,
                'priority': 3,
                'type': 'api',
                'timeout': 8,
                'description': 'Cars & Bids - Enthusiast car auctions'
            },
            'facebook_marketplace': {
                'enabled': True,
                'priority': 4,
                'type': 'user_submission',
                'timeout': 2,
                'description': 'Facebook Marketplace - User-submitted listings (ToS compliant)'
            },
            'craigslist': {
                'enabled': True,
                'priority': 5,
                'type': 'rss',
                'timeout': 10,
                'description': 'Craigslist - Local private party listings'
            },
            'revy_autos': {
                'enabled': True,
                'priority': 6,
                'type': 'api',
                'timeout': 8,
                'description': 'Revy Autos - Modern car marketplace'
            },
            'carsoup': {
                'enabled': True,
                'priority': 7,
                'type': 'scrape',
                'timeout': 10,
                'description': 'CarSoup - Midwest regional marketplace'
            },
            'carmax': {
                'enabled': True,
                'priority': 8,
                'type': 'scrape',
                'timeout': 15,
                'description': 'CarMax - Used car superstore'
            },
            'autotrader': {
                'enabled': True,
                'priority': 9,
                'type': 'scrape',
                'timeout': 15,
                'description': 'AutoTrader - Popular vehicle marketplace'
            },
            'cargurus': {
                'enabled': False,  # Disabled due to anti-bot
                'priority': 10,
                'type': 'scrape',
                'timeout': 15,
                'description': 'CarGurus - Price analysis marketplace'
            },
            'truecar': {
                'enabled': False,  # Disabled due to anti-bot
                'priority': 10,
                'type': 'scrape',
                'timeout': 15,
                'description': 'TrueCar - Transparent pricing platform'
            },
            # Future sources
            'carvana': {
                'enabled': True,
                'priority': 11,
                'type': 'api',
                'timeout': 10,
                'description': 'Carvana - Online car retailer'
            },
            'cars_com': {
                'enabled': True,
                'priority': 12,
                'type': 'api',
                'timeout': 10,
                'description': 'Cars.com via Marketcheck - Comprehensive marketplace'
            },
            'autobytel': {
                'enabled': True,
                'priority': 13,
                'type': 'api',
                'timeout': 10,
                'description': 'Autobytel/AutoWeb - B2B dealer network'
            },
            'autotrader_ca': {
                'enabled': False,
                'priority': 14,
                'type': 'scrape',
                'timeout': 10,
                'description': 'AutoTrader.ca - Canadian marketplace'
            },
            'carsdirect': {
                'enabled': True,
                'priority': 15,
                'type': 'api',
                'timeout': 10,
                'description': 'CarsDirect - Affiliate network with dealer pricing'
            },
            'private_auto': {
                'enabled': False,
                'priority': 16,
                'type': 'api',
                'timeout': 10,
                'description': 'PrivateAuto - Secure private sales'
            }
        }
    
    def _initialize_sources(self) -> Dict:
        """
        Initialize all available source clients
        """
        sources = {}
        
        try:
            # API-based sources
            if os.getenv('EBAY_CLIENT_ID'):
                sources['ebay'] = EbayLiveClient()
                logger.info("Initialized eBay client")
        except Exception as e:
            logger.error(f"Failed to initialize eBay client: {e}")
        
        try:
            # RSS-based sources
            sources['hemmings'] = HemmingsClient()
            sources['craigslist'] = CraigslistClient()
            logger.info("Initialized RSS-based clients")
        except Exception as e:
            logger.error(f"Failed to initialize RSS clients: {e}")
        
        try:
            # API sources
            sources['cars_bids'] = CarsBidsClient()
            sources['facebook_marketplace'] = FacebookMarketplaceClient()
            sources['revy_autos'] = RevyAutosClient()
            logger.info("Initialized API-based clients")
        except Exception as e:
            logger.error(f"Failed to initialize API clients: {e}")
        
        try:
            # Scraping sources
            sources['carsoup'] = CarSoupClient()
            sources['carmax'] = CarMaxWrapper()
            sources['autotrader'] = AutoTraderWrapper()
            logger.info("Initialized scraping clients")
        except Exception as e:
            logger.error(f"Failed to initialize scraping clients: {e}")
        
        # Try problematic sources with caution
        if os.getenv('ENABLE_RISKY_SOURCES') == 'true':
            try:
                sources['cargurus'] = CarGurusClient()
                sources['truecar'] = TrueCarClient()
            except Exception as e:
                logger.warning(f"Failed to initialize risky sources: {e}")
        
        # Initialize Phase 2 sources
        try:
            # Carvana - no API key required
            sources['carvana'] = CarvanaClient()
            logger.info("Initialized Carvana client")
        except Exception as e:
            logger.error(f"Failed to initialize Carvana client: {e}")
        
        try:
            # Cars.com via Marketcheck API
            if os.getenv('MARKETCHECK_API_KEY'):
                sources['cars_com'] = CarsComClient()
                logger.info("Initialized Cars.com client (Marketcheck)")
        except Exception as e:
            logger.error(f"Failed to initialize Cars.com client: {e}")
        
        try:
            # Autobytel/AutoWeb
            if os.getenv('AUTOWEB_PARTNER_ID') and os.getenv('AUTOWEB_API_KEY'):
                sources['autobytel'] = AutobytelClient()
                logger.info("Initialized Autobytel client")
        except Exception as e:
            logger.error(f"Failed to initialize Autobytel client: {e}")
        
        try:
            # CarsDirect
            if os.getenv('CARSDIRECT_AFFILIATE_ID'):
                sources['carsdirect'] = CarsDirectClient()
                logger.info("Initialized CarsDirect client")
        except Exception as e:
            logger.error(f"Failed to initialize CarsDirect client: {e}")
        
        return sources
    
    def get_enabled_sources(self) -> List[str]:
        """
        Get list of currently enabled sources
        """
        return [
            name for name, config in self.source_config.items()
            if config['enabled'] and name in self.sources
        ]
    
    def search_all_sources(self, query: str = "", make: Optional[str] = None,
                          model: Optional[str] = None, year_min: Optional[int] = None,
                          year_max: Optional[int] = None, price_min: Optional[float] = None,
                          price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                          page: int = 1, per_page: int = 20,
                          sources: Optional[List[str]] = None) -> Dict:
        """
        Search all enabled sources in parallel
        """
        # Determine which sources to search
        if sources:
            search_sources = [s for s in sources if s in self.get_enabled_sources()]
        else:
            search_sources = self.get_enabled_sources()
        
        if not search_sources:
            return {
                'vehicles': [],
                'total': 0,
                'sources_searched': [],
                'sources_failed': [],
                'search_time': 0
            }
        
        # Sort by priority
        search_sources.sort(key=lambda x: self.source_config[x]['priority'])
        
        logger.info(f"Searching {len(search_sources)} sources: {search_sources}")
        
        start_time = datetime.now()
        all_results = []
        sources_succeeded = []
        sources_failed = []
        
        # Search sources in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(
                    self._search_source,
                    source,
                    query, make, model, year_min, year_max,
                    price_min, price_max, mileage_max, page, per_page
                ): source
                for source in search_sources
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    result = future.result(timeout=self.source_config[source]['timeout'])
                    if result and result.get('vehicles'):
                        all_results.append(result)
                        sources_succeeded.append(source)
                        logger.info(f"Source {source} returned {len(result['vehicles'])} vehicles")
                except Exception as e:
                    sources_failed.append(source)
                    logger.error(f"Source {source} failed: {str(e)}")
        
        # Merge and deduplicate results
        merged_vehicles = self._merge_and_dedupe_results(all_results)
        
        # Sort by relevance/date
        merged_vehicles.sort(key=lambda x: x.get('created_date', ''), reverse=True)
        
        # Apply pagination on merged results
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_vehicles = merged_vehicles[start_idx:end_idx]
        
        search_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'vehicles': paginated_vehicles,
            'total': len(merged_vehicles),
            'page': page,
            'per_page': per_page,
            'sources_searched': sources_succeeded,
            'sources_failed': sources_failed,
            'search_time': search_time,
            'source_details': {
                source: self.source_config[source]['description']
                for source in sources_succeeded
            }
        }
    
    def _search_source(self, source: str, query: str, make: Optional[str],
                      model: Optional[str], year_min: Optional[int],
                      year_max: Optional[int], price_min: Optional[float],
                      price_max: Optional[float], mileage_max: Optional[int],
                      page: int, per_page: int) -> Optional[Dict]:
        """
        Search a single source with error handling
        """
        try:
            client = self.sources.get(source)
            if not client:
                logger.warning(f"Source {source} client not found")
                return None
            
            # Check cache first if available
            cache_key = f"{source}:{query}:{make}:{model}:{year_min}:{year_max}:{price_min}:{price_max}:{page}"
            
            if self.cache_manager:
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info(f"Cache hit for {source}")
                    return cached_result
            
            # Perform search
            result = client.search_vehicles(
                query=query,
                make=make,
                model=model,
                year_min=year_min,
                year_max=year_max,
                price_min=price_min,
                price_max=price_max,
                page=page,
                per_page=50  # Get more from each source
            )
            
            # Add source metadata to each vehicle
            if result and result.get('vehicles'):
                for vehicle in result['vehicles']:
                    vehicle['source_metadata'] = {
                        'source': source,
                        'source_type': self.source_config[source]['type'],
                        'retrieved_at': datetime.now().isoformat()
                    }
            
            # Cache successful results
            if self.cache_manager and result:
                cache_ttl = 300 if self.source_config[source]['type'] == 'api' else 600
                self.cache_manager.set(cache_key, result, ttl=cache_ttl)
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching {source}: {str(e)}\n{traceback.format_exc()}")
            return None
    
    def _merge_and_dedupe_results(self, results: List[Dict]) -> List[Dict]:
        """
        Merge results from multiple sources and remove duplicates
        """
        all_vehicles = []
        seen_vehicles = set()
        
        for result in results:
            for vehicle in result.get('vehicles', []):
                # Create unique key based on make, model, year, price, and location
                vehicle_key = self._generate_vehicle_key(vehicle)
                
                if vehicle_key not in seen_vehicles:
                    seen_vehicles.add(vehicle_key)
                    all_vehicles.append(vehicle)
                else:
                    # If duplicate, prefer the one with more information
                    existing_idx = next(
                        (i for i, v in enumerate(all_vehicles) 
                         if self._generate_vehicle_key(v) == vehicle_key),
                        None
                    )
                    if existing_idx is not None:
                        existing = all_vehicles[existing_idx]
                        if self._count_fields(vehicle) > self._count_fields(existing):
                            all_vehicles[existing_idx] = vehicle
        
        return all_vehicles
    
    def _generate_vehicle_key(self, vehicle: Dict) -> str:
        """
        Generate a unique key for deduplication
        """
        make = (vehicle.get('make') or '').lower()
        model = (vehicle.get('model') or '').lower()
        year = vehicle.get('year') or 0
        price = vehicle.get('price') or 0
        mileage = vehicle.get('mileage') or 0
        
        # Round price and mileage to handle minor differences
        price_rounded = round(price / 100) * 100 if price else 0
        mileage_rounded = round(mileage / 1000) * 1000 if mileage else 0
        
        return f"{make}:{model}:{year}:{price_rounded}:{mileage_rounded}"
    
    def _count_fields(self, vehicle: Dict) -> int:
        """
        Count non-null fields in a vehicle record
        """
        return sum(1 for v in vehicle.values() if v is not None)
    
    def check_all_sources_health(self) -> Dict:
        """
        Check health of all sources
        """
        health_status = {}
        
        for source_name, client in self.sources.items():
            if hasattr(client, 'check_health'):
                try:
                    health_status[source_name] = client.check_health()
                except Exception as e:
                    health_status[source_name] = {
                        'source': source_name,
                        'status': 'error',
                        'message': str(e)
                    }
            else:
                health_status[source_name] = {
                    'source': source_name,
                    'status': 'unknown',
                    'message': 'Health check not implemented'
                }
        
        return health_status
    
    def enable_source(self, source: str):
        """
        Enable a specific source
        """
        if source in self.source_config:
            self.source_config[source]['enabled'] = True
            logger.info(f"Enabled source: {source}")
    
    def disable_source(self, source: str):
        """
        Disable a specific source
        """
        if source in self.source_config:
            self.source_config[source]['enabled'] = False
            logger.info(f"Disabled source: {source}")
    
    def get_source_stats(self) -> Dict:
        """
        Get statistics about available sources
        """
        total_sources = len(self.source_config)
        enabled_sources = len(self.get_enabled_sources())
        
        source_types = {}
        for config in self.source_config.values():
            source_type = config['type']
            source_types[source_type] = source_types.get(source_type, 0) + 1
        
        return {
            'total_sources': total_sources,
            'enabled_sources': enabled_sources,
            'disabled_sources': total_sources - enabled_sources,
            'source_types': source_types,
            'sources': {
                name: {
                    'enabled': config['enabled'],
                    'type': config['type'],
                    'description': config['description']
                }
                for name, config in self.source_config.items()
            }
        }