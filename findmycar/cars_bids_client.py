"""
Cars & Bids Auction Platform Client
API endpoints now require authentication - using fallback data approach
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class CarsBidsClient:
    """
    Client for accessing Cars & Bids auction listings
    NOTE: API endpoints require authentication as of July 2024
    Currently returns fallback data to maintain API compatibility
    """
    BASE_URL = "https://carsandbids.com"
    
    # API endpoints now require authentication tokens
    PROTECTED_API_URL = "https://carsandbids.com/api/v2"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://carsandbids.com/'
        })
        self._fallback_data = self._generate_fallback_data()
    
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, page: int = 1,
                       per_page: int = 20) -> Dict:
        """
        Search Cars & Bids auctions - currently returns fallback data due to API authentication
        """
        try:
            logger.warning("Cars & Bids API requires authentication - returning fallback data")
            
            # Use fallback data until API access is restored
            vehicles = []
            for vehicle in self._fallback_data:
                if self._matches_filters(vehicle, query, make, model,
                                       year_min, year_max, price_min, price_max):
                    vehicles.append(vehicle)
            
            # Apply pagination on filtered results
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_vehicles = vehicles[start_idx:end_idx]
            
            return {
                'vehicles': paginated_vehicles,
                'total': len(vehicles),
                'page': page,
                'per_page': per_page,
                'source': 'cars_bids',
                'warning': 'Using fallback data - API requires authentication'
            }
            
        except Exception as e:
            logger.error(f"Error searching Cars & Bids: {str(e)}")
            return self._empty_response()
    
    def _parse_auction(self, auction: Dict) -> Optional[Dict]:
        """
        Parse auction data into vehicle dict
        """
        try:
            car = auction.get('car', {})
            
            # Extract current bid as price
            current_bid = auction.get('current_bid', 0)
            
            # Parse ending time
            ends_at = auction.get('ends_at')
            if ends_at:
                ends_at_dt = datetime.fromisoformat(ends_at.replace('Z', '+00:00'))
                time_left = ends_at_dt - datetime.now(ends_at_dt.tzinfo)
                days_left = time_left.days
                hours_left = time_left.seconds // 3600
                time_left_str = f"{days_left}d {hours_left}h" if days_left > 0 else f"{hours_left}h"
            else:
                time_left_str = "Unknown"
            
            # Get primary image
            images = car.get('images', [])
            primary_image = images[0]['url'] if images else None
            
            return {
                'id': f"cars_bids_{auction.get('id', '')}",
                'title': f"{car.get('year', '')} {car.get('make', '')} {car.get('model', '')}".strip(),
                'price': current_bid,
                'year': car.get('year'),
                'make': car.get('make'),
                'model': car.get('model'),
                'mileage': car.get('mileage'),
                'location': f"{car.get('city', '')}, {car.get('state', '')}".strip(', '),
                'link': f"{self.BASE_URL}{auction.get('url', '')}",
                'image': primary_image,
                'description': car.get('highlights', ''),
                'source': 'cars_bids',
                'condition': 'Used',
                'seller_type': auction.get('seller_type', 'Private Party'),
                'created_date': auction.get('created_at', datetime.now().isoformat()),
                'body_style': car.get('body_style'),
                'exterior_color': car.get('exterior_color'),
                'interior_color': car.get('interior_color'),
                'engine': car.get('engine'),
                'transmission': car.get('transmission'),
                'drivetrain': car.get('drivetrain'),
                'vin': car.get('vin'),
                'auction_info': {
                    'current_bid': current_bid,
                    'bid_count': auction.get('bid_count', 0),
                    'ends_at': ends_at,
                    'time_left': time_left_str,
                    'reserve_met': auction.get('reserve_met', False),
                    'has_reserve': auction.get('has_reserve', True)
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing Cars & Bids auction: {str(e)}")
            return None
    
    def _matches_filters(self, vehicle: Dict, query: str, make: Optional[str],
                        model: Optional[str], year_min: Optional[int],
                        year_max: Optional[int], price_min: Optional[float],
                        price_max: Optional[float]) -> bool:
        """
        Check if vehicle matches search filters
        """
        # Text search
        if query:
            searchable_text = f"{vehicle.get('title', '')} {vehicle.get('description', '')}".lower()
            if query.lower() not in searchable_text:
                return False
        
        # Make filter
        if make and vehicle.get('make'):
            if make.lower() != vehicle['make'].lower():
                return False
        
        # Model filter
        if model and vehicle.get('model'):
            if model.lower() not in vehicle['model'].lower():
                return False
        
        # Year filters
        if year_min and vehicle.get('year'):
            if vehicle['year'] < year_min:
                return False
        if year_max and vehicle.get('year'):
            if vehicle['year'] > year_max:
                return False
        
        # Price filters (using current bid)
        if price_min and vehicle.get('price'):
            if vehicle['price'] < price_min:
                return False
        if price_max and vehicle.get('price'):
            if vehicle['price'] > price_max:
                return False
        
        return True
    
    def _generate_fallback_data(self) -> List[Dict]:
        """
        Generate fallback auction data for when API is unavailable
        Returns representative Cars & Bids auction listings
        """
        fallback_auctions = [
            {
                'id': 'cars_bids_fallback_1',
                'title': '2019 BMW M2 Competition',
                'price': 55000,  # Current bid
                'year': 2019,
                'make': 'BMW',
                'model': 'M2',
                'mileage': 12500,
                'location': 'Los Angeles, CA',
                'link': 'https://carsandbids.com/auctions/K8rqm5gX/2019-bmw-m2-competition',
                'image': 'https://via.placeholder.com/300x200.png?text=2019+BMW+M2',
                'description': 'No Reserve: 2019 BMW M2 Competition with 6-speed manual transmission. Original owner with full service history.',
                'source': 'cars_bids',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Coupe',
                'exterior_color': 'Alpine White',
                'interior_color': 'Black',
                'engine': '3.0L Twin-Turbo I6',
                'transmission': '6-Speed Manual',
                'drivetrain': 'RWD',
                'auction_info': {
                    'current_bid': 55000,
                    'bid_count': 23,
                    'ends_at': '2024-07-21T20:00:00Z',
                    'time_left': '1d 8h',
                    'reserve_met': False,
                    'has_reserve': True
                }
            },
            {
                'id': 'cars_bids_fallback_2',
                'title': '1993 Porsche 911 Turbo',
                'price': 125000,
                'year': 1993,
                'make': 'Porsche',
                'model': '911',
                'mileage': 45000,
                'location': 'Miami, FL',
                'link': 'https://carsandbids.com/auctions/9Xm3q2wE/1993-porsche-911-turbo',
                'image': 'https://via.placeholder.com/300x200.png?text=1993+Porsche+911',
                'description': '1993 Porsche 911 Turbo with rare color combination. Comprehensive service records and recent major maintenance.',
                'source': 'cars_bids',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Coupe',
                'exterior_color': 'Guards Red',
                'interior_color': 'Black Leather',
                'engine': '3.6L Turbo Flat-6',
                'transmission': '5-Speed Manual',
                'drivetrain': 'AWD',
                'auction_info': {
                    'current_bid': 125000,
                    'bid_count': 41,
                    'ends_at': '2024-07-22T19:30:00Z',
                    'time_left': '2d 7h',
                    'reserve_met': True,
                    'has_reserve': True
                }
            },
            {
                'id': 'cars_bids_fallback_3',
                'title': '2021 Ford Bronco First Edition',
                'price': 68000,
                'year': 2021,
                'make': 'Ford',
                'model': 'Bronco',
                'mileage': 8500,
                'location': 'Austin, TX',
                'link': 'https://carsandbids.com/auctions/L5pq8nR4/2021-ford-bronco-first-edition',
                'image': 'https://via.placeholder.com/300x200.png?text=2021+Ford+Bronco',
                'description': 'No Reserve: 2021 Ford Bronco First Edition in rare Cactus Gray. Factory hardtop and soft top included.',
                'source': 'cars_bids',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': datetime.now().isoformat(),
                'body_style': 'SUV',
                'exterior_color': 'Cactus Gray',
                'interior_color': 'Black',
                'engine': '2.7L EcoBoost V6',
                'transmission': '10-Speed Automatic',
                'drivetrain': '4WD',
                'auction_info': {
                    'current_bid': 68000,
                    'bid_count': 18,
                    'ends_at': '2024-07-20T21:15:00Z',
                    'time_left': '18h',
                    'reserve_met': False,
                    'has_reserve': False
                }
            },
            {
                'id': 'cars_bids_fallback_4',
                'title': '2020 Tesla Model S Performance',
                'price': 78000,
                'year': 2020,
                'make': 'Tesla',
                'model': 'Model S',
                'mileage': 22000,
                'location': 'Seattle, WA',
                'link': 'https://carsandbids.com/auctions/M9dx7tK2/2020-tesla-model-s-performance',
                'image': 'https://via.placeholder.com/300x200.png?text=2020+Tesla+Model+S',
                'description': '2020 Tesla Model S Performance with Ludicrous mode. Full self-driving capability and premium interior.',
                'source': 'cars_bids',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Sedan',
                'exterior_color': 'Pearl White',
                'interior_color': 'White',
                'engine': 'Electric (Dual Motor)',
                'transmission': 'Single-Speed',
                'drivetrain': 'AWD',
                'auction_info': {
                    'current_bid': 78000,
                    'bid_count': 32,
                    'ends_at': '2024-07-23T20:45:00Z',
                    'time_left': '3d 12h',
                    'reserve_met': True,
                    'has_reserve': True
                }
            },
            {
                'id': 'cars_bids_fallback_5',
                'title': '1995 Toyota Supra Turbo',
                'price': 95000,
                'year': 1995,
                'make': 'Toyota',
                'model': 'Supra',
                'mileage': 67000,
                'location': 'Phoenix, AZ',
                'link': 'https://carsandbids.com/auctions/N3hv6bP9/1995-toyota-supra-turbo',
                'image': 'https://via.placeholder.com/300x200.png?text=1995+Toyota+Supra',
                'description': 'Pristine 1995 Toyota Supra Turbo with 6-speed manual. All original with extensive documentation.',
                'source': 'cars_bids',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': datetime.now().isoformat(),
                'body_style': 'Coupe',
                'exterior_color': 'Renaissance Red',
                'interior_color': 'Black',
                'engine': '3.0L Twin-Turbo I6',
                'transmission': '6-Speed Manual',
                'drivetrain': 'RWD',
                'auction_info': {
                    'current_bid': 95000,
                    'bid_count': 56,
                    'ends_at': '2024-07-24T19:00:00Z',
                    'time_left': '4d 11h',
                    'reserve_met': False,
                    'has_reserve': True
                }
            }
        ]
        
        logger.info(f"Generated {len(fallback_auctions)} fallback Cars & Bids auctions")
        return fallback_auctions
    
    def _empty_response(self) -> Dict:
        """
        Return empty response structure
        """
        return {
            'vehicles': [],
            'total': 0,
            'page': 1,
            'per_page': 20,
            'source': 'cars_bids'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific auction
        """
        try:
            # Extract auction ID
            if vehicle_id.startswith('cars_bids_'):
                auction_id = vehicle_id.replace('cars_bids_', '')
                url = f"{self.API_URL}/auctions/{auction_id}"
                
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    auction_data = response.json()
                    return self._parse_auction(auction_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting auction details: {str(e)}")
            return None
    
    def get_completed_sales(self, make: Optional[str] = None, 
                           model: Optional[str] = None) -> List[Dict]:
        """
        Get completed sales data for market analysis
        """
        try:
            url = f"{self.API_URL}/auctions"
            params = {
                'status': 'completed',
                'sort': 'recently_ended',
                'per_page': 100
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return []
            
            data = response.json()
            completed_auctions = []
            
            for auction in data.get('auctions', []):
                car = auction.get('car', {})
                
                # Filter by make/model if specified
                if make and car.get('make', '').lower() != make.lower():
                    continue
                if model and model.lower() not in car.get('model', '').lower():
                    continue
                
                # Only include if it sold (has winning bid)
                if auction.get('winning_bid'):
                    completed_auctions.append({
                        'year': car.get('year'),
                        'make': car.get('make'),
                        'model': car.get('model'),
                        'sale_price': auction.get('winning_bid'),
                        'sale_date': auction.get('ends_at'),
                        'mileage': car.get('mileage'),
                        'condition': 'Used',
                        'link': f"{self.BASE_URL}{auction.get('url', '')}"
                    })
            
            return completed_auctions
            
        except Exception as e:
            logger.error(f"Error getting completed sales: {str(e)}")
            return []
    
    def check_health(self) -> Dict:
        """
        Check Cars & Bids client status - currently using fallback data due to authentication
        """
        try:
            # Test website accessibility
            response = self.session.get(self.BASE_URL, timeout=5)
            website_accessible = response.status_code == 200
            
            # Test API endpoint to confirm authentication requirement
            api_response = self.session.get(f"{self.PROTECTED_API_URL}/auctions", timeout=5)
            api_requires_auth = api_response.status_code == 403
            
            fallback_count = len(self._fallback_data)
            
            return {
                'source': 'cars_bids',
                'status': 'degraded',  # Functional but using fallback data
                'response_time': response.elapsed.total_seconds() if website_accessible else 0,
                'message': f"Website accessible, using {fallback_count} fallback auctions (API requires authentication)",
                'details': {
                    'website_accessible': website_accessible,
                    'api_requires_auth': api_requires_auth,
                    'fallback_auctions': fallback_count
                }
            }
        except Exception as e:
            return {
                'source': 'cars_bids',
                'status': 'unhealthy',
                'response_time': 0,
                'message': f"Website inaccessible: {str(e)}",
                'details': {
                    'website_accessible': False,
                    'api_requires_auth': True,
                    'fallback_auctions': len(self._fallback_data)
                }
            }