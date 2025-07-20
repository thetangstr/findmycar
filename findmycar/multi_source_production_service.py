#!/usr/bin/env python3
"""
Production search service with multiple live data sources
Includes eBay API, CarMax scraping, and AutoTrader scraping
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ebay_live_client import EbayLiveClient
from carmax_client import CarMaxClient
from autotrader_client import AutotraderClient
from cargurus_client import CarGurusClient

logger = logging.getLogger(__name__)

class MultiSourceProductionService:
    """
    Production service that aggregates data from multiple sources
    """
    
    def __init__(self):
        # Initialize clients
        self.ebay_client = EbayLiveClient()
        self.carmax_client = None  # Lazy init due to Selenium
        self.autotrader_client = None  # Lazy init due to Selenium
        self.cargurus_client = None  # Lazy init due to Selenium
        
        # Thread lock for Selenium clients
        self._selenium_lock = threading.Lock()
        
        # Source configuration
        self.source_config = {
            'ebay': {
                'enabled': True,
                'type': 'api',
                'rate_limit': 10,  # requests per second
                'timeout': 30
            },
            'carmax': {
                'enabled': True,
                'type': 'scraping',
                'rate_limit': 0.5,  # requests per second (slower for scraping)
                'timeout': 60
            },
            'autotrader': {
                'enabled': True,
                'type': 'scraping',
                'rate_limit': 0.5,
                'timeout': 60
            },
            'cargurus': {
                'enabled': False,  # Currently not working well
                'type': 'scraping',
                'rate_limit': 0.3,
                'timeout': 60
            }
        }
    
    def _get_carmax_client(self):
        """Lazy initialization of CarMax client"""
        if self.carmax_client is None:
            with self._selenium_lock:
                if self.carmax_client is None:
                    self.carmax_client = CarMaxClient()
        return self.carmax_client
    
    def _get_autotrader_client(self):
        """Lazy initialization of AutoTrader client"""
        if self.autotrader_client is None:
            with self._selenium_lock:
                if self.autotrader_client is None:
                    self.autotrader_client = AutotraderClient()
        return self.autotrader_client
    
    def search_all_sources(self, 
                          query: str,
                          filters: Optional[Dict[str, Any]] = None,
                          limit_per_source: int = 20) -> Dict[str, Any]:
        """
        Search all enabled sources concurrently
        """
        start_time = datetime.utcnow()
        filters = filters or {}
        
        # Results container
        all_results = {
            'vehicles': [],
            'sources': {},
            'errors': {},
            'timing': {}
        }
        
        # Use ThreadPoolExecutor for concurrent searches
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            # Submit search tasks for each enabled source
            if self.source_config['ebay']['enabled']:
                future = executor.submit(
                    self._search_ebay,
                    query, filters, limit_per_source
                )
                futures[future] = 'ebay'
            
            if self.source_config['carmax']['enabled']:
                future = executor.submit(
                    self._search_carmax,
                    query, filters, limit_per_source
                )
                futures[future] = 'carmax'
            
            if self.source_config['autotrader']['enabled']:
                future = executor.submit(
                    self._search_autotrader,
                    query, filters, limit_per_source
                )
                futures[future] = 'autotrader'
            
            # Collect results as they complete
            for future in as_completed(futures, timeout=90):
                source = futures[future]
                source_start = datetime.utcnow()
                
                try:
                    result = future.result()
                    all_results['sources'][source] = {
                        'count': len(result),
                        'status': 'success'
                    }
                    all_results['vehicles'].extend(result)
                    
                except Exception as e:
                    logger.error(f"Error searching {source}: {e}")
                    all_results['sources'][source] = {
                        'count': 0,
                        'status': 'error',
                        'error': str(e)
                    }
                    all_results['errors'][source] = str(e)
                
                finally:
                    source_end = datetime.utcnow()
                    all_results['timing'][source] = (source_end - source_start).total_seconds()
        
        # Deduplicate vehicles
        all_results['vehicles'] = self._deduplicate_vehicles(all_results['vehicles'])
        
        # Calculate total time
        end_time = datetime.utcnow()
        all_results['total_time'] = (end_time - start_time).total_seconds()
        all_results['total_vehicles'] = len(all_results['vehicles'])
        
        return all_results
    
    def _search_ebay(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Search eBay using API"""
        try:
            logger.info(f"Searching eBay for: {query}")
            
            results = self.ebay_client.search_vehicles(
                query=query,
                make=filters.get('make'),
                model=filters.get('model'),
                year_min=filters.get('year_min'),
                year_max=filters.get('year_max'),
                price_min=filters.get('price_min'),
                price_max=filters.get('price_max'),
                mileage_max=filters.get('mileage_max'),
                per_page=limit
            )
            
            vehicles = results.get('vehicles', [])
            logger.info(f"eBay returned {len(vehicles)} vehicles")
            
            # Add source info
            for vehicle in vehicles:
                vehicle['source'] = 'ebay'
                vehicle['source_type'] = 'api'
                
            return vehicles
            
        except Exception as e:
            logger.error(f"eBay search error: {e}")
            raise
    
    def _search_carmax(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Search CarMax using web scraping"""
        try:
            logger.info(f"Searching CarMax for: {query}")
            
            client = self._get_carmax_client()
            vehicles = client.search_listings(
                query=query,
                filters=filters,
                limit=limit
            )
            
            logger.info(f"CarMax returned {len(vehicles)} vehicles")
            
            # Add source info and ensure consistent format
            for vehicle in vehicles:
                vehicle['source'] = 'carmax'
                vehicle['source_type'] = 'scraping'
                
                # Ensure price is float
                if vehicle.get('price') and isinstance(vehicle['price'], str):
                    vehicle['price'] = float(vehicle['price'].replace(',', '').replace('$', ''))
                
            return vehicles
            
        except Exception as e:
            logger.error(f"CarMax search error: {e}")
            raise
    
    def _search_autotrader(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Search AutoTrader using web scraping"""
        try:
            logger.info(f"Searching AutoTrader for: {query}")
            
            client = self._get_autotrader_client()
            vehicles = client.search_listings(
                query=query,
                filters=filters,
                limit=limit
            )
            
            logger.info(f"AutoTrader returned {len(vehicles)} vehicles")
            
            # Add source info
            for vehicle in vehicles:
                vehicle['source'] = 'autotrader'
                vehicle['source_type'] = 'scraping'
                
                # Ensure consistent format
                if vehicle.get('price') and isinstance(vehicle['price'], str):
                    vehicle['price'] = float(vehicle['price'].replace(',', '').replace('$', ''))
                
            return vehicles
            
        except Exception as e:
            logger.error(f"AutoTrader search error: {e}")
            raise
    
    def _deduplicate_vehicles(self, vehicles: List[Dict]) -> List[Dict]:
        """
        Deduplicate vehicles based on listing characteristics
        """
        seen = set()
        unique_vehicles = []
        
        for vehicle in vehicles:
            # Create a unique key based on vehicle attributes
            key_parts = [
                str(vehicle.get('year', '')),
                vehicle.get('make', '').lower(),
                vehicle.get('model', '').lower(),
                str(vehicle.get('price', '')),
                str(vehicle.get('mileage', '')),
                vehicle.get('source', '')
            ]
            
            # For vehicles with listing IDs, include that too
            if vehicle.get('listing_id'):
                key_parts.append(str(vehicle['listing_id']))
            
            key = '|'.join(key_parts)
            
            if key not in seen:
                seen.add(key)
                unique_vehicles.append(vehicle)
        
        return unique_vehicles
    
    def get_source_status(self) -> Dict[str, Any]:
        """Get current status of all data sources"""
        status = {}
        
        for source, config in self.source_config.items():
            status[source] = {
                'enabled': config['enabled'],
                'type': config['type'],
                'rate_limit': config['rate_limit'],
                'health': 'unknown'
            }
            
            # Check health for enabled sources
            if config['enabled']:
                if source == 'ebay':
                    # Check if we have API credentials
                    try:
                        import os
                        if os.environ.get('EBAY_CLIENT_ID'):
                            status[source]['health'] = 'healthy'
                        else:
                            status[source]['health'] = 'missing_credentials'
                    except Exception:
                        status[source]['health'] = 'error'
                        
                elif source in ['carmax', 'autotrader']:
                    # These use Selenium, so they're generally available
                    status[source]['health'] = 'healthy'
                    status[source]['note'] = 'Uses web scraping - may be slow'
        
        return status
    
    def cleanup(self):
        """Clean up resources (close Selenium drivers)"""
        if self.carmax_client:
            try:
                self.carmax_client.close()
            except Exception as e:
                logger.error(f"Error closing CarMax client: {e}")
        
        if self.autotrader_client:
            try:
                self.autotrader_client.close()
            except Exception as e:
                logger.error(f"Error closing AutoTrader client: {e}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    service = MultiSourceProductionService()
    
    # Get source status
    print("Data Source Status:")
    status = service.get_source_status()
    for source, info in status.items():
        print(f"  {source}: {info['health']} ({info['type']})")
    
    # Search all sources
    print("\nSearching all sources for 'Honda Civic'...")
    results = service.search_all_sources(
        query="Honda Civic",
        filters={
            'year_min': 2015,
            'price_max': 25000
        },
        limit_per_source=10
    )
    
    print(f"\nResults:")
    print(f"  Total vehicles: {results['total_vehicles']}")
    print(f"  Total time: {results['total_time']:.2f}s")
    print(f"\n  By source:")
    for source, info in results['sources'].items():
        print(f"    {source}: {info['count']} vehicles ({info['status']})")
        if 'error' in info:
            print(f"      Error: {info['error']}")
    
    print(f"\n  First 5 vehicles:")
    for vehicle in results['vehicles'][:5]:
        print(f"    - {vehicle.get('year')} {vehicle.get('make')} {vehicle.get('model')} "
              f"${vehicle.get('price'):,.0f} ({vehicle.get('source')})")
    
    # Cleanup
    service.cleanup()