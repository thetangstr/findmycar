"""
Facebook Marketplace Client
Safe implementation using user-submitted listings approach
Does not attempt direct scraping to comply with Facebook ToS
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class FacebookMarketplaceClient:
    """
    Client for Facebook Marketplace vehicle listings via user submissions
    This approach complies with Facebook's Terms of Service by not scraping
    """
    
    BASE_URL = "https://www.facebook.com/marketplace"
    
    def __init__(self):
        # Storage for user-submitted listings (in production, this would be a database)
        self._user_submissions = []
        self._sample_data = self._generate_sample_data()
        
    def search_vehicles(self, query: str = "", make: Optional[str] = None,
                       model: Optional[str] = None, year_min: Optional[int] = None,
                       year_max: Optional[int] = None, price_min: Optional[float] = None,
                       price_max: Optional[float] = None, page: int = 1,
                       per_page: int = 20) -> Dict:
        """
        Search Facebook Marketplace listings from user submissions
        """
        try:
            logger.info(f"Searching Facebook Marketplace submissions for: {query or 'all vehicles'}")
            
            # Combine user submissions with sample data
            all_listings = self._user_submissions + self._sample_data
            
            vehicles = []
            for listing in all_listings:
                if self._matches_filters(listing, query, make, model,
                                       year_min, year_max, price_min, price_max):
                    vehicles.append(listing)
            
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_vehicles = vehicles[start_idx:end_idx]
            
            return {
                'vehicles': paginated_vehicles,
                'total': len(vehicles),
                'page': page,
                'per_page': per_page,
                'source': 'facebook_marketplace',
                'note': 'Data from user submissions and samples - direct scraping not performed'
            }
            
        except Exception as e:
            logger.error(f"Error searching Facebook Marketplace: {str(e)}")
            return self._empty_response()
    
    def submit_listing(self, user_id: str, listing_data: Dict) -> Dict:
        """
        Allow users to submit Facebook Marketplace listings they find
        This is the safe, ToS-compliant way to get Facebook data
        """
        try:
            # Validate the listing data
            if not self._validate_listing(listing_data):
                return {
                    'success': False,
                    'message': 'Invalid listing data provided'
                }
            
            # Clean and standardize the data
            cleaned_listing = self._clean_listing_data(listing_data, user_id)
            
            # Add to submissions (in production, save to database)
            self._user_submissions.append(cleaned_listing)
            
            logger.info(f"Added user-submitted Facebook listing: {cleaned_listing.get('title')}")
            
            return {
                'success': True,
                'message': 'Listing submitted successfully',
                'listing_id': cleaned_listing['id']
            }
            
        except Exception as e:
            logger.error(f"Error submitting listing: {str(e)}")
            return {
                'success': False,
                'message': f'Submission failed: {str(e)}'
            }
    
    def _validate_listing(self, listing_data: Dict) -> bool:
        """
        Validate user-submitted listing data
        """
        required_fields = ['title', 'price', 'url']
        
        for field in required_fields:
            if field not in listing_data or not listing_data[field]:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate URL is from Facebook Marketplace
        url = listing_data.get('url', '')
        if not self._is_facebook_marketplace_url(url):
            logger.warning(f"Invalid Facebook Marketplace URL: {url}")
            return False
        
        # Validate price is a number
        try:
            float(str(listing_data['price']).replace('$', '').replace(',', ''))
        except (ValueError, TypeError):
            logger.warning(f"Invalid price format: {listing_data.get('price')}")
            return False
        
        return True
    
    def _is_facebook_marketplace_url(self, url: str) -> bool:
        """
        Check if URL is a valid Facebook Marketplace listing
        """
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc in ['www.facebook.com', 'facebook.com', 'm.facebook.com'] and
                '/marketplace/' in parsed.path
            )
        except:
            return False
    
    def _clean_listing_data(self, listing_data: Dict, user_id: str) -> Dict:
        """
        Clean and standardize user-submitted listing data
        """
        # Extract vehicle details from title if possible
        title = listing_data.get('title', '')
        year = self._extract_year(title)
        make = self._extract_make(title)
        model = self._extract_model(title, make)
        
        # Clean price
        price_str = str(listing_data.get('price', '0'))
        price = float(re.sub(r'[^\d.]', '', price_str)) if re.search(r'\d', price_str) else 0
        
        # Generate unique ID
        listing_id = f"facebook_{hash(listing_data.get('url', ''))}"
        
        return {
            'id': listing_id,
            'title': title,
            'price': price,
            'year': year,
            'make': make,
            'model': model,
            'mileage': listing_data.get('mileage'),
            'location': listing_data.get('location', 'Unknown'),
            'link': listing_data.get('url'),
            'image': listing_data.get('image_url'),
            'description': listing_data.get('description', '')[:200],
            'source': 'facebook_marketplace',
            'condition': listing_data.get('condition', 'Used'),
            'seller_type': 'Private Party',  # Most Facebook listings are private
            'created_date': datetime.now().isoformat(),
            'body_style': listing_data.get('body_style'),
            'exterior_color': listing_data.get('color'),
            'submitted_by': user_id,
            'submission_date': datetime.now().isoformat()
        }
    
    def _extract_year(self, title: str) -> Optional[int]:
        """Extract year from title"""
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', title)
        return int(year_match.group(1)) if year_match else None
    
    def _extract_make(self, title: str) -> Optional[str]:
        """Extract make from title"""
        # Common car makes
        makes = [
            'Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes', 'Audi',
            'Volkswagen', 'Hyundai', 'Kia', 'Mazda', 'Subaru', 'Lexus', 'Infiniti',
            'Acura', 'Cadillac', 'Lincoln', 'Buick', 'GMC', 'Dodge', 'Chrysler', 'Jeep',
            'Ram', 'Volvo', 'Jaguar', 'Land Rover', 'Porsche', 'Tesla', 'Mitsubishi'
        ]
        
        title_lower = title.lower()
        for make in makes:
            if make.lower() in title_lower:
                return make
        
        return None
    
    def _extract_model(self, title: str, make: Optional[str]) -> Optional[str]:
        """Extract model from title"""
        if not make:
            return None
        
        # Remove year and make from title to isolate model
        title_clean = title
        title_clean = re.sub(r'\b(19\d{2}|20\d{2})\b', '', title_clean)
        title_clean = title_clean.replace(make, '', 1)
        
        # Extract first 1-2 words as potential model
        words = title_clean.strip().split()[:2]
        model = ' '.join(words).strip()
        
        return model if model else None
    
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
        
        # Price filters
        if price_min and vehicle.get('price'):
            if vehicle['price'] < price_min:
                return False
        if price_max and vehicle.get('price'):
            if vehicle['price'] > price_max:
                return False
        
        return True
    
    def _generate_sample_data(self) -> List[Dict]:
        """
        Generate sample Facebook Marketplace listings for demonstration
        """
        sample_listings = [
            {
                'id': 'facebook_sample_1',
                'title': '2018 Honda Civic LX',
                'price': 18500,
                'year': 2018,
                'make': 'Honda',
                'model': 'Civic',
                'mileage': 45000,
                'location': 'Los Angeles, CA',
                'link': 'https://www.facebook.com/marketplace/item/sample1',
                'image': 'https://via.placeholder.com/300x200.png?text=2018+Honda+Civic',
                'description': 'Well-maintained 2018 Honda Civic LX. Single owner, clean title, recent oil change.',
                'source': 'facebook_marketplace',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': (datetime.now() - timedelta(days=2)).isoformat(),
                'body_style': 'Sedan',
                'exterior_color': 'Silver'
            },
            {
                'id': 'facebook_sample_2',
                'title': '2020 Ford F-150 XLT',
                'price': 32000,
                'year': 2020,
                'make': 'Ford',
                'model': 'F-150',
                'mileage': 28000,
                'location': 'Dallas, TX',
                'link': 'https://www.facebook.com/marketplace/item/sample2',
                'image': 'https://via.placeholder.com/300x200.png?text=2020+Ford+F150',
                'description': '2020 Ford F-150 XLT SuperCab. Great condition, towing package, bed liner included.',
                'source': 'facebook_marketplace',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': (datetime.now() - timedelta(days=1)).isoformat(),
                'body_style': 'Truck',
                'exterior_color': 'Blue'
            },
            {
                'id': 'facebook_sample_3',
                'title': '2019 Toyota Camry SE',
                'price': 22000,
                'year': 2019,
                'make': 'Toyota',
                'model': 'Camry',
                'mileage': 35000,
                'location': 'Miami, FL',
                'link': 'https://www.facebook.com/marketplace/item/sample3',
                'image': 'https://via.placeholder.com/300x200.png?text=2019+Toyota+Camry',
                'description': 'Excellent condition 2019 Toyota Camry SE. Sporty trim with paddle shifters.',
                'source': 'facebook_marketplace',
                'condition': 'Used',
                'seller_type': 'Private Party',
                'created_date': (datetime.now() - timedelta(hours=12)).isoformat(),
                'body_style': 'Sedan',
                'exterior_color': 'Red'
            }
        ]
        
        logger.info(f"Generated {len(sample_listings)} sample Facebook Marketplace listings")
        return sample_listings
    
    def _empty_response(self) -> Dict:
        """
        Return empty response structure
        """
        return {
            'vehicles': [],
            'total': 0,
            'page': 1,
            'per_page': 20,
            'source': 'facebook_marketplace'
        }
    
    def get_vehicle_details(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific vehicle
        """
        try:
            all_listings = self._user_submissions + self._sample_data
            
            for listing in all_listings:
                if listing.get('id') == vehicle_id:
                    return listing
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting vehicle details: {str(e)}")
            return None
    
    def get_submission_stats(self) -> Dict:
        """
        Get statistics about user submissions
        """
        return {
            'total_submissions': len(self._user_submissions),
            'sample_listings': len(self._sample_data),
            'total_available': len(self._user_submissions) + len(self._sample_data),
            'last_submission': self._user_submissions[-1]['submission_date'] if self._user_submissions else None
        }
    
    def check_health(self) -> Dict:
        """
        Check Facebook Marketplace client status
        """
        try:
            total_listings = len(self._user_submissions) + len(self._sample_data)
            
            return {
                'source': 'facebook_marketplace',
                'status': 'healthy',  # Always healthy since it doesn't depend on external APIs
                'response_time': 0.1,  # Local data access is fast
                'message': f"User submission system active with {total_listings} listings",
                'details': {
                    'user_submissions': len(self._user_submissions),
                    'sample_listings': len(self._sample_data),
                    'total_listings': total_listings,
                    'scraping_compliance': 'ToS compliant - no direct scraping'
                }
            }
        except Exception as e:
            return {
                'source': 'facebook_marketplace',
                'status': 'unhealthy',
                'response_time': 0,
                'message': str(e)
            }