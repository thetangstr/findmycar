"""
Enhanced eBay data extraction with comprehensive attribute parsing
"""

import re
import logging
from typing import Dict, List, Any, Optional
from attribute_standardizer import AttributeStandardizer

logger = logging.getLogger(__name__)


class EbayEnhancedExtractor:
    """Extract maximum data from eBay Motors API responses"""
    
    def __init__(self):
        self.standardizer = AttributeStandardizer()
        
        # Common eBay itemSpecific names to look for
        self.important_specs = {
            # Core
            'Make', 'Model', 'Year', 'Mileage', 'VIN',
            
            # Body & Style
            'Body Type', 'Exterior Color', 'Interior Color',
            'Number of Doors', 'Vehicle Title',
            
            # Mechanical
            'Engine', 'Number of Cylinders', 'Transmission',
            'Drive Type', 'Fuel Type',
            
            # Features & Options
            'Options', 'Safety Features', 'Power Options',
            'Interior Features', 'Exterior Features',
            'Technology Features', 'Convenience Features',
            
            # History
            'Accident History', 'Service History', 'Previous Owners',
            'Title Status', 'Warranty',
            
            # Performance
            'City MPG', 'Highway MPG', 'Combined MPG',
            'Engine Size', 'Horsepower', 'Torque'
        }
    
    def extract_all_data(self, ebay_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all possible data from an eBay item
        
        Returns standardized data structure ready for VehicleV2
        """
        # Start with basic extraction
        extracted = {
            'listing_id': f"v1|{ebay_item.get('itemId', '')}",
            'source': 'ebay',
            'title': ebay_item.get('title', ''),
            'price': self._extract_price(ebay_item),
            'location': self._extract_location(ebay_item),
            'view_item_url': ebay_item.get('itemWebUrl', ''),
            'condition': ebay_item.get('condition', ''),
            'seller': self._extract_seller_info(ebay_item),
        }
        
        # Extract all item specifics into a dict
        specs = self._extract_all_item_specifics(ebay_item)
        
        # Use standardizer to process the data
        standardized = self.standardizer.standardize_vehicle_data({
            **extracted,
            'itemSpecifics': ebay_item.get('localizedAspects', []),
            'shortDescription': ebay_item.get('shortDescription', ''),
            'description': self._extract_description_text(ebay_item),
            **specs
        }, 'ebay')
        
        # Extract additional eBay-specific data
        enhanced_data = {
            # Core fields
            'make': standardized['core_fields'].get('make') or specs.get('Make'),
            'model': standardized['core_fields'].get('model') or specs.get('Model'),
            'year': standardized['core_fields'].get('year') or self._parse_year(specs.get('Year')),
            'mileage': standardized['core_fields'].get('mileage') or self._parse_mileage(specs.get('Mileage')),
            
            # All other core fields from standardizer
            **standardized['core_fields'],
            
            # Location data
            'location': extracted['location'],
            'zip_code': self._extract_zip_from_location(extracted['location']),
            
            # Images
            'image_urls': self._extract_all_images(ebay_item),
            
            # JSONB fields
            'attributes': {
                **standardized['attributes'],
                **self._extract_technical_specs(specs),
                **self._extract_seller_attributes(ebay_item),
            },
            'features': self._merge_features(
                standardized['features'],
                self._extract_features_from_options(specs.get('Options', '')),
                self._extract_features_from_safety(specs.get('Safety Features', ''))
            ),
            'history': {
                **standardized['history'],
                **self._extract_history_data(specs),
            },
            
            # Pricing analysis
            'pricing_analysis': self._extract_pricing_data(ebay_item),
            
            # Raw data
            'raw_data': ebay_item
        }
        
        return enhanced_data
    
    def _extract_all_item_specifics(self, item: Dict[str, Any]) -> Dict[str, str]:
        """Extract all item specifics into a simple dict"""
        specs = {}
        
        # Modern API format
        for aspect in item.get('localizedAspects', []):
            if 'localizedName' in aspect and 'localizedValues' in aspect:
                name = aspect['localizedName']
                values = aspect['localizedValues']
                if values:
                    specs[name] = values[0]['value']
        
        # Legacy format support
        for spec in item.get('itemSpecifics', []):
            if 'name' in spec and 'value' in spec:
                specs[spec['name']] = spec['value']
        
        return specs
    
    def _extract_price(self, item: Dict[str, Any]) -> Optional[float]:
        """Extract price from various eBay formats"""
        # Current price
        if 'price' in item and 'value' in item['price']:
            return float(item['price']['value'])
        
        # Buy it now price
        if 'buyingOptions' in item and 'FIXED_PRICE' in item['buyingOptions']:
            if 'currentBidPrice' in item:
                return float(item['currentBidPrice']['value'])
        
        return None
    
    def _extract_location(self, item: Dict[str, Any]) -> Optional[str]:
        """Extract location information"""
        if 'itemLocation' in item:
            location = item['itemLocation']
            if isinstance(location, dict):
                parts = []
                if 'city' in location:
                    parts.append(location['city'])
                if 'stateOrProvince' in location:
                    parts.append(location['stateOrProvince'])
                if 'postalCode' in location:
                    parts.append(location['postalCode'])
                return ', '.join(parts)
            else:
                return location
        return None
    
    def _extract_seller_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract seller information"""
        seller_info = {}
        
        if 'seller' in item:
            seller = item['seller']
            seller_info['username'] = seller.get('username')
            seller_info['feedback_score'] = seller.get('feedbackScore')
            seller_info['feedback_percentage'] = seller.get('feedbackPercentage')
        
        return seller_info
    
    def _extract_all_images(self, item: Dict[str, Any]) -> List[str]:
        """Extract all available images"""
        images = []
        
        # Primary image
        if 'image' in item and 'imageUrl' in item['image']:
            images.append(item['image']['imageUrl'])
        
        # Additional images
        if 'additionalImages' in item:
            for img in item['additionalImages']:
                if 'imageUrl' in img:
                    images.append(img['imageUrl'])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_images = []
        for img in images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)
        
        return unique_images
    
    def _extract_description_text(self, item: Dict[str, Any]) -> str:
        """Extract and clean description text"""
        description = item.get('description', '')
        
        # Remove HTML if present
        if '<' in description and '>' in description:
            # Simple HTML stripping
            description = re.sub(r'<[^>]+>', ' ', description)
            description = re.sub(r'\s+', ' ', description)
        
        return description.strip()
    
    def _extract_technical_specs(self, specs: Dict[str, str]) -> Dict[str, Any]:
        """Extract technical specifications"""
        tech_specs = {}
        
        # Engine details
        if 'Engine' in specs:
            engine_info = self._parse_engine_details(specs['Engine'])
            tech_specs.update(engine_info)
        
        # Transmission details
        if 'Transmission' in specs:
            trans_info = self._parse_transmission_details(specs['Transmission'])
            tech_specs.update(trans_info)
        
        # Dimensions
        dimension_keys = ['Length', 'Width', 'Height', 'Wheelbase', 'Curb Weight']
        for key in dimension_keys:
            if key in specs:
                clean_key = key.lower().replace(' ', '_')
                tech_specs[clean_key] = self._parse_dimension(specs[key])
        
        return tech_specs
    
    def _parse_engine_details(self, engine_str: str) -> Dict[str, Any]:
        """Parse engine string for details"""
        details = {}
        
        # Engine size (e.g., "3.5L", "350 cu in")
        size_match = re.search(r'(\d+\.?\d*)\s*[Ll]', engine_str)
        if size_match:
            details['engine_size_liters'] = float(size_match.group(1))
        
        # Cylinder config (e.g., "V6", "V8", "I4")
        config_match = re.search(r'([VvIi]\d+)', engine_str)
        if config_match:
            details['engine_config'] = config_match.group(1).upper()
        
        # Turbo/Supercharged
        if any(term in engine_str.lower() for term in ['turbo', 'turbocharged']):
            details['forced_induction'] = 'turbo'
        elif any(term in engine_str.lower() for term in ['supercharged', 'supercharger']):
            details['forced_induction'] = 'supercharged'
        
        return details
    
    def _parse_transmission_details(self, trans_str: str) -> Dict[str, Any]:
        """Parse transmission string for details"""
        details = {}
        
        # Number of speeds
        speed_match = re.search(r'(\d+)[-\s]?speed', trans_str.lower())
        if speed_match:
            details['transmission_speeds'] = int(speed_match.group(1))
        
        return details
    
    def _extract_features_from_options(self, options_str: str) -> List[str]:
        """Extract features from Options field"""
        if not options_str:
            return []
        
        features = []
        
        # Common option patterns
        option_patterns = {
            'leather_seats': r'leather\s*(seats|interior)',
            'navigation': r'navigation|nav\s*system|gps',
            'sunroof': r'sunroof|moonroof|panoramic\s*roof',
            'backup_camera': r'backup\s*camera|rear\s*camera|rearview\s*camera',
            'heated_seats': r'heated\s*seats',
            'cooled_seats': r'cooled\s*seats|ventilated\s*seats',
            'premium_audio': r'premium\s*(audio|sound)|bose|harman|bang\s*&\s*olufsen',
            'keyless_entry': r'keyless\s*entry|smart\s*key',
            'remote_start': r'remote\s*start',
            'parking_sensors': r'parking\s*sensors|park\s*assist',
            'third_row': r'third\s*row|3rd\s*row|7\s*passenger',
            'tow_package': r'tow(ing)?\s*package|trailer\s*hitch',
            'alloy_wheels': r'alloy\s*wheels|aluminum\s*wheels',
        }
        
        options_lower = options_str.lower()
        for feature, pattern in option_patterns.items():
            if re.search(pattern, options_lower):
                features.append(feature)
        
        return features
    
    def _extract_features_from_safety(self, safety_str: str) -> List[str]:
        """Extract features from Safety Features field"""
        if not safety_str:
            return []
        
        features = []
        
        safety_patterns = {
            'abs': r'abs|anti[\s-]?lock',
            'stability_control': r'stability\s*control|esc|electronic\s*stability',
            'traction_control': r'traction\s*control',
            'blind_spot_monitor': r'blind\s*spot|bsm|blind\s*spot\s*monitoring',
            'lane_departure': r'lane\s*(departure|warning|keep)',
            'collision_warning': r'collision\s*(warning|alert|mitigation)',
            'adaptive_cruise': r'adaptive\s*cruise|radar\s*cruise',
            'automatic_braking': r'automatic\s*braking|emergency\s*braking|aeb',
            'airbags_side': r'side\s*airbags?|side\s*curtain',
            'airbags_front': r'front\s*airbags?|driver\s*airbag',
        }
        
        safety_lower = safety_str.lower()
        for feature, pattern in safety_patterns.items():
            if re.search(pattern, safety_lower):
                features.append(feature)
        
        return features
    
    def _extract_history_data(self, specs: Dict[str, str]) -> Dict[str, Any]:
        """Extract vehicle history information"""
        history = {}
        
        # Accident history
        if 'Accident History' in specs:
            history['accident_reported'] = 'no accident' not in specs['Accident History'].lower()
        
        # Service records
        if 'Service History' in specs:
            history['service_records_available'] = 'available' in specs['Service History'].lower()
        
        # Previous owners
        if 'Previous Owners' in specs or 'Number of Owners' in specs:
            owner_str = specs.get('Previous Owners') or specs.get('Number of Owners', '')
            owner_match = re.search(r'(\d+)', owner_str)
            if owner_match:
                history['previous_owners'] = int(owner_match.group(1))
        
        # Title status
        if 'Vehicle Title' in specs:
            title = specs['Vehicle Title'].lower()
            history['clean_title'] = 'clean' in title or 'clear' in title
            history['salvage_title'] = 'salvage' in title
            history['rebuilt_title'] = 'rebuilt' in title or 'reconstructed' in title
        
        return history
    
    def _extract_pricing_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pricing and market data"""
        pricing = {}
        
        # Current price
        if 'price' in item:
            pricing['current_price'] = float(item['price'].get('value', 0))
            pricing['currency'] = item['price'].get('currency', 'USD')
        
        # Market comparison (placeholder for future enhancement)
        pricing['price_analysis'] = 'market_price'  # Could be: below_market, market_price, above_market
        
        # Bidding info if auction
        if 'bidCount' in item:
            pricing['bid_count'] = item['bidCount']
        
        if 'currentBidPrice' in item:
            pricing['current_bid'] = float(item['currentBidPrice'].get('value', 0))
        
        return pricing
    
    def _extract_seller_attributes(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract seller-related attributes"""
        attrs = {}
        
        if 'seller' in item:
            seller = item['seller']
            if seller.get('feedbackScore', 0) > 1000:
                attrs['trusted_seller'] = True
            if seller.get('feedbackPercentage', 0) >= 99:
                attrs['top_rated_seller'] = True
        
        return attrs
    
    def _merge_features(self, *feature_lists) -> List[str]:
        """Merge multiple feature lists and deduplicate"""
        all_features = []
        for feature_list in feature_lists:
            if feature_list:
                all_features.extend(feature_list)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_features = []
        for feature in all_features:
            if feature not in seen:
                seen.add(feature)
                unique_features.append(feature)
        
        return unique_features
    
    def _parse_year(self, year_str: Any) -> Optional[int]:
        """Parse year from string"""
        if not year_str:
            return None
        try:
            return int(str(year_str)[:4])
        except:
            return None
    
    def _parse_mileage(self, mileage_str: Any) -> Optional[int]:
        """Parse mileage from string"""
        if not mileage_str:
            return None
        try:
            # Remove non-numeric characters
            cleaned = re.sub(r'[^\d]', '', str(mileage_str))
            return int(cleaned) if cleaned else None
        except:
            return None
    
    def _parse_dimension(self, dim_str: str) -> Optional[float]:
        """Parse dimension value from string"""
        if not dim_str:
            return None
        
        # Look for number with optional decimal
        match = re.search(r'(\d+\.?\d*)', dim_str)
        if match:
            return float(match.group(1))
        
        return None
    
    def _extract_zip_from_location(self, location: Optional[str]) -> Optional[str]:
        """Extract ZIP code from location string"""
        if not location:
            return None
        
        # Look for 5-digit ZIP
        match = re.search(r'\b\d{5}\b', location)
        return match.group() if match else None