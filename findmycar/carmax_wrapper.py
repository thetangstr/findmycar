"""
Wrapper for CarMax client to standardize interface
"""
from carmax_client import CarMaxClient
from typing import Dict, Optional

class CarMaxWrapper:
    def __init__(self):
        self.client = CarMaxClient()
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, mileage_max: Optional[int] = None,
                       page: int = 1, per_page: int = 20) -> Dict:
        """
        Wrapper to match the standard search interface
        """
        filters = {}
        if make:
            filters['make'] = make
        if model:
            filters['model'] = model
        if year_min:
            filters['year_min'] = year_min
        if year_max:
            filters['year_max'] = year_max
        if price_min:
            filters['price_min'] = price_min
        if price_max:
            filters['price_max'] = price_max
        if mileage_max:
            filters['mileage_max'] = mileage_max
        
        offset = (page - 1) * per_page
        
        try:
            vehicles = self.client.search_listings(
                query=query,
                filters=filters,
                limit=per_page,
                offset=offset
            )
            
            return {
                'vehicles': vehicles,
                'total': len(vehicles),  # CarMax doesn't provide total
                'page': page,
                'per_page': per_page,
                'source': 'carmax'
            }
        except Exception as e:
            return {
                'vehicles': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'source': 'carmax',
                'error': str(e)
            }
    
    def check_health(self) -> Dict:
        """Health check for CarMax"""
        return {
            'source': 'carmax',
            'status': 'unknown',
            'message': 'Health check not implemented'
        }