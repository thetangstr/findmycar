"""
Attribute standardization system for normalizing vehicle data across sources
"""

import re
from typing import Dict, List, Any, Optional
import logging
from database_v2_sqlite import ATTRIBUTE_MAPPINGS, FEATURE_MAPPINGS

logger = logging.getLogger(__name__)


class AttributeStandardizer:
    """Standardizes vehicle attributes from various sources into consistent format"""
    
    def __init__(self):
        self.attribute_mappings = ATTRIBUTE_MAPPINGS
        self.feature_mappings = FEATURE_MAPPINGS
        
        # Build reverse mappings for fast lookup
        self.attribute_lookup = {}
        for standard_name, variations in self.attribute_mappings.items():
            for variation in variations:
                self.attribute_lookup[variation.lower()] = standard_name
        
        self.feature_lookup = {}
        for standard_name, variations in self.feature_mappings.items():
            for variation in variations:
                self.feature_lookup[variation.lower()] = standard_name
    
    def standardize_vehicle_data(self, raw_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Standardize vehicle data from any source into consistent format
        
        Returns:
            {
                'core_fields': {...},  # Direct database columns
                'attributes': {...},   # JSONB attributes field
                'features': [...],     # JSONB features array
                'history': {...}       # JSONB history field
            }
        """
        standardized = {
            'core_fields': {},
            'attributes': {},
            'features': [],
            'history': {}
        }
        
        # Source-specific extraction
        if source == 'ebay':
            standardized = self._standardize_ebay(raw_data)
        elif source == 'carmax':
            standardized = self._standardize_carmax(raw_data)
        elif source == 'cargurus':
            standardized = self._standardize_cargurus(raw_data)
        else:
            # Generic extraction
            standardized = self._standardize_generic(raw_data)
        
        # Post-process all sources
        standardized['attributes'] = self._clean_attributes(standardized['attributes'])
        standardized['features'] = self._deduplicate_features(standardized['features'])
        
        return standardized
    
    def _standardize_ebay(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize eBay Motors data"""
        result = {
            'core_fields': {},
            'attributes': {},
            'features': [],
            'history': {}
        }
        
        # Extract from itemSpecifics
        item_specifics = data.get('itemSpecifics', [])
        specs_dict = {}
        
        for spec in item_specifics:
            if 'localizedName' in spec and 'value' in spec:
                name = spec['localizedName']
                value = spec['value']
                specs_dict[name] = value
        
        # Core fields
        result['core_fields'] = {
            'make': specs_dict.get('Make'),
            'model': specs_dict.get('Model'),
            'year': self._parse_year(specs_dict.get('Year')),
            'mileage': self._parse_mileage(specs_dict.get('Mileage')),
            'transmission': self._standardize_transmission(specs_dict.get('Transmission')),
            'drivetrain': self._standardize_drivetrain(specs_dict.get('Drive Type')),
            'fuel_type': self._standardize_fuel_type(specs_dict.get('Fuel Type')),
            'body_style': self._standardize_body_style(specs_dict.get('Body Type')),
            'exterior_color': self._standardize_color(specs_dict.get('Exterior Color')),
            'interior_color': self._standardize_color(specs_dict.get('Interior Color')),
        }
        
        # Attributes
        result['attributes'] = {
            'vin': specs_dict.get('VIN'),
            'engine': specs_dict.get('Engine'),
            'cylinders': self._parse_cylinders(specs_dict.get('Number of Cylinders')),
            'doors': self._parse_doors(specs_dict.get('Number of Doors')),
            'mpg_city': self._parse_mpg(specs_dict.get('City MPG')),
            'mpg_highway': self._parse_mpg(specs_dict.get('Highway MPG')),
            'title_status': specs_dict.get('Vehicle Title'),
            'condition': specs_dict.get('Condition'),
        }
        
        # Extract features from Options field
        options = specs_dict.get('Options', '')
        features = self._extract_features_from_text(options)
        
        # Extract features from description
        description = data.get('shortDescription', '') + ' ' + data.get('description', '')
        features.extend(self._extract_features_from_text(description))
        
        result['features'] = features
        
        # History
        result['history'] = {
            'title_status': specs_dict.get('Vehicle Title'),
            'accident_history': specs_dict.get('Accident History'),
            'service_history': specs_dict.get('Service History'),
        }
        
        return result
    
    def _standardize_carmax(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize CarMax data"""
        result = {
            'core_fields': {},
            'attributes': {},
            'features': [],
            'history': {}
        }
        
        # Core fields
        result['core_fields'] = {
            'make': data.get('make'),
            'model': data.get('model'),
            'year': data.get('year'),
            'mileage': data.get('mileage'),
            'transmission': self._standardize_transmission(data.get('transmissionType')),
            'drivetrain': self._standardize_drivetrain(data.get('driveType')),
            'fuel_type': self._standardize_fuel_type(data.get('fuelType')),
            'body_style': self._standardize_body_style(data.get('bodyStyle')),
            'exterior_color': self._standardize_color(data.get('exteriorColor')),
            'interior_color': self._standardize_color(data.get('interiorColor')),
        }
        
        # Attributes
        result['attributes'] = {
            'mpg_city': data.get('mpgCity'),
            'mpg_highway': data.get('mpgHighway'),
            'seating_capacity': data.get('seatingCapacity'),
            'certified': data.get('certified', False),
            'photo_count': data.get('photoCount'),
        }
        
        # Features
        features_list = data.get('features', [])
        result['features'] = self._standardize_features_list(features_list)
        
        # History
        result['history'] = {
            'carfax_available': data.get('carfaxAvailable'),
            'one_owner': data.get('oneOwner'),
            'clean_title': data.get('cleanTitle'),
        }
        
        return result
    
    def _standardize_generic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic standardization for unknown sources"""
        result = {
            'core_fields': {},
            'attributes': {},
            'features': [],
            'history': {}
        }
        
        # Try to extract core fields from common keys
        result['core_fields'] = {
            'make': data.get('make') or data.get('Make'),
            'model': data.get('model') or data.get('Model'),
            'year': self._parse_year(data.get('year') or data.get('Year')),
            'mileage': self._parse_mileage(data.get('mileage') or data.get('Mileage')),
            'price': self._parse_price(data.get('price') or data.get('Price')),
        }
        
        # Look for attributes using our mapping
        for key, value in data.items():
            standard_key = self.attribute_lookup.get(key.lower())
            if standard_key:
                result['attributes'][standard_key] = value
        
        # Extract features from any text fields
        text_fields = ['description', 'features', 'options', 'equipment']
        combined_text = ' '.join(str(data.get(field, '')) for field in text_fields)
        result['features'] = self._extract_features_from_text(combined_text)
        
        return result
    
    def _standardize_transmission(self, transmission: Optional[str]) -> Optional[str]:
        """Standardize transmission types"""
        if not transmission:
            return None
            
        trans_lower = transmission.lower()
        
        if any(term in trans_lower for term in ['manual', 'stick', 'm/t', '5-speed', '6-speed']):
            return 'manual'
        elif any(term in trans_lower for term in ['cvt', 'continuously variable']):
            return 'cvt'
        elif any(term in trans_lower for term in ['dct', 'dual clutch', 'dsg', 'pdk']):
            return 'dual-clutch'
        elif any(term in trans_lower for term in ['auto', 'automatic', 'a/t']):
            return 'automatic'
        
        return transmission
    
    def _standardize_drivetrain(self, drivetrain: Optional[str]) -> Optional[str]:
        """Standardize drivetrain types"""
        if not drivetrain:
            return None
            
        drive_lower = drivetrain.lower()
        
        if any(term in drive_lower for term in ['awd', 'all wheel', 'all-wheel']):
            return 'awd'
        elif any(term in drive_lower for term in ['4wd', '4x4', 'four wheel', '4 wheel']):
            return '4wd'
        elif any(term in drive_lower for term in ['fwd', 'front wheel', 'front-wheel']):
            return 'fwd'
        elif any(term in drive_lower for term in ['rwd', 'rear wheel', 'rear-wheel']):
            return 'rwd'
        
        return drivetrain
    
    def _standardize_fuel_type(self, fuel: Optional[str]) -> Optional[str]:
        """Standardize fuel types"""
        if not fuel:
            return None
            
        fuel_lower = fuel.lower()
        
        if any(term in fuel_lower for term in ['electric', 'ev', 'battery']):
            return 'electric'
        elif any(term in fuel_lower for term in ['plug-in hybrid', 'plug in hybrid', 'phev']):
            return 'plug-in hybrid'
        elif any(term in fuel_lower for term in ['hybrid', 'hev']):
            return 'hybrid'
        elif any(term in fuel_lower for term in ['diesel', 'tdi']):
            return 'diesel'
        elif any(term in fuel_lower for term in ['flex', 'e85']):
            return 'flex-fuel'
        elif any(term in fuel_lower for term in ['gas', 'gasoline', 'petrol']):
            return 'gasoline'
        
        return fuel
    
    def _standardize_body_style(self, body: Optional[str]) -> Optional[str]:
        """Standardize body styles"""
        if not body:
            return None
            
        body_lower = body.lower()
        
        if any(term in body_lower for term in ['sedan', 'saloon']):
            return 'sedan'
        elif any(term in body_lower for term in ['suv', 'sport utility', 'crossover']):
            return 'suv'
        elif any(term in body_lower for term in ['truck', 'pickup']):
            return 'truck'
        elif any(term in body_lower for term in ['coupe', '2 door', '2-door']):
            return 'coupe'
        elif any(term in body_lower for term in ['convertible', 'cabriolet', 'roadster']):
            return 'convertible'
        elif any(term in body_lower for term in ['hatchback', 'hatch']):
            return 'hatchback'
        elif any(term in body_lower for term in ['wagon', 'estate']):
            return 'wagon'
        elif any(term in body_lower for term in ['van', 'minivan']):
            return 'van'
        
        return body
    
    def _standardize_color(self, color: Optional[str]) -> Optional[str]:
        """Standardize color names"""
        if not color:
            return None
            
        color_lower = color.lower()
        
        # Map variations to standard colors
        color_map = {
            'black': ['black', 'ebony', 'onyx', 'midnight', 'carbon'],
            'white': ['white', 'pearl', 'snow', 'arctic', 'alabaster'],
            'silver': ['silver', 'metallic', 'titanium', 'gunmetal'],
            'gray': ['gray', 'grey', 'graphite', 'charcoal'],
            'blue': ['blue', 'navy', 'azure', 'sapphire', 'cobalt'],
            'red': ['red', 'crimson', 'burgundy', 'maroon', 'ruby'],
            'green': ['green', 'emerald', 'forest', 'jade', 'mint'],
            'brown': ['brown', 'bronze', 'mocha', 'chocolate', 'espresso'],
            'beige': ['beige', 'tan', 'sand', 'champagne', 'cream'],
            'gold': ['gold', 'golden', 'brass'],
            'yellow': ['yellow', 'lemon'],
            'orange': ['orange', 'copper', 'rust'],
        }
        
        for standard, variations in color_map.items():
            if any(var in color_lower for var in variations):
                return standard
        
        return color
    
    def _extract_features_from_text(self, text: str) -> List[str]:
        """Extract standardized features from text"""
        if not text:
            return []
            
        text_lower = text.lower()
        found_features = []
        
        for standard_feature, variations in self.feature_mappings.items():
            for variation in variations:
                if variation in text_lower:
                    found_features.append(standard_feature)
                    break
        
        return found_features
    
    def _standardize_features_list(self, features: List[str]) -> List[str]:
        """Standardize a list of features"""
        standardized = []
        
        for feature in features:
            feature_lower = feature.lower()
            standard_feature = self.feature_lookup.get(feature_lower)
            
            if standard_feature:
                standardized.append(standard_feature)
            else:
                # Check if any variation matches
                for std_feat, variations in self.feature_mappings.items():
                    if any(var in feature_lower for var in variations):
                        standardized.append(std_feat)
                        break
        
        return list(set(standardized))  # Remove duplicates
    
    def _parse_year(self, year_str: Any) -> Optional[int]:
        """Parse year from various formats"""
        if not year_str:
            return None
        try:
            return int(str(year_str)[:4])
        except:
            return None
    
    def _parse_mileage(self, mileage_str: Any) -> Optional[int]:
        """Parse mileage from various formats"""
        if not mileage_str:
            return None
        try:
            # Remove non-numeric characters
            cleaned = re.sub(r'[^\d]', '', str(mileage_str))
            return int(cleaned) if cleaned else None
        except:
            return None
    
    def _parse_price(self, price_str: Any) -> Optional[float]:
        """Parse price from various formats"""
        if not price_str:
            return None
        try:
            # Remove non-numeric characters except decimal
            cleaned = re.sub(r'[^\d.]', '', str(price_str))
            return float(cleaned) if cleaned else None
        except:
            return None
    
    def _parse_cylinders(self, cyl_str: Any) -> Optional[int]:
        """Parse number of cylinders"""
        if not cyl_str:
            return None
        try:
            # Extract first number
            match = re.search(r'\d+', str(cyl_str))
            return int(match.group()) if match else None
        except:
            return None
    
    def _parse_doors(self, door_str: Any) -> Optional[int]:
        """Parse number of doors"""
        if not door_str:
            return None
        try:
            # Extract first number
            match = re.search(r'\d+', str(door_str))
            return int(match.group()) if match else None
        except:
            return None
    
    def _parse_mpg(self, mpg_str: Any) -> Optional[int]:
        """Parse MPG value"""
        if not mpg_str:
            return None
        try:
            # Extract first number
            match = re.search(r'\d+', str(mpg_str))
            return int(match.group()) if match else None
        except:
            return None
    
    def _clean_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None values and clean attributes"""
        return {k: v for k, v in attributes.items() if v is not None}
    
    def _deduplicate_features(self, features: List[str]) -> List[str]:
        """Remove duplicate features"""
        return list(set(features))