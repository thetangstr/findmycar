"""
Vehicle Attribute Inference System

This module infers vehicle attributes (body style, transmission, fuel type, etc.)
from various data sources that may have different field names or missing data.
"""

import re
from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)

class VehicleAttributeInferencer:
    """Infers vehicle attributes from various data sources."""
    
    def __init__(self):
        # Model to body style mapping
        self.model_body_style_map = {
            # SUVs and Crossovers
            'suv': ['explorer', 'tahoe', 'suburban', 'expedition', 'pilot', 'highlander', 
                   'pathfinder', '4runner', 'wrangler', 'cherokee', 'grand cherokee',
                   'durango', 'traverse', 'atlas', 'telluride', 'palisade', 'ascent',
                   'outback', 'forester', 'crosstrek', 'cr-v', 'rav4', 'rogue',
                   'escape', 'edge', 'blazer', 'equinox', 'terrain', 'encore',
                   'trax', 'ecosport', 'bronco', 'defender', 'discovery', 'range rover',
                   'x3', 'x5', 'x7', 'q3', 'q5', 'q7', 'gla', 'glb', 'glc', 'gle',
                   'macan', 'cayenne', 'model x', 'model y', 'mach-e', 'id.4'],
            
            # Trucks and Pickups
            'truck': ['f-150', 'f-250', 'f-350', 'silverado', 'sierra', 'ram',
                     'tundra', 'tacoma', 'frontier', 'ranger', 'colorado', 'canyon',
                     'ridgeline', 'gladiator', 'maverick', 'santa cruz', 'cybertruck'],
            
            # Sedans
            'sedan': ['accord', 'camry', 'corolla', 'civic', 'sentra', 'altima',
                     'malibu', 'impala', 'fusion', 'taurus', 'charger', 'challenger',
                     '3 series', '5 series', '7 series', 'a4', 'a6', 'a8', 'c-class',
                     'e-class', 's-class', 'model 3', 'model s', 'panamera', 'ghibli',
                     'giulia', 'genesis', 'stinger', 'optima', 'sonata', 'elantra',
                     'jetta', 'passat', 'arteon'],
            
            # Hatchbacks
            'hatchback': ['golf', 'gti', 'focus', 'fiesta', 'mazda3', 'impreza',
                         'wrx', 'veloster', 'rio', 'yaris', 'fit', 'versa', 'leaf',
                         'bolt', 'i3', 'mini cooper', 'fiat 500', 'spark', 'sonic'],
            
            # Convertibles and Roadsters
            'convertible': ['miata', 'mx-5', 'boxster', 'cayman', '911', 'corvette',
                           'mustang convertible', 'camaro convertible', 'z4', '4 series convertible',
                           'c-class convertible', 'e-class convertible', 's5 convertible',
                           'tt roadster', 'spider', 'spyder', 'roadster', 'cabrio', 'cabriolet'],
            
            # Coupes
            'coupe': ['mustang', 'camaro', 'challenger', 'charger', 'brz', 'gr86',
                     '86', 'supra', '370z', '400z', 'q60', 'rc', '4 series',
                     '8 series', 'c-class coupe', 'e-class coupe', 's5', 'tt'],
            
            # Vans and Minivans
            'van': ['odyssey', 'pacifica', 'sienna', 'carnival', 'quest',
                   'transit', 'sprinter', 'promaster', 'express', 'savana',
                   'metris', 'transit connect', 'promaster city'],
            
            # Wagons
            'wagon': ['outback', 'alltrack', 'sportwagen', 'v60', 'v90',
                     'e-class wagon', 'panamera sport turismo', 'rs6 avant']
        }
        
        # Title keywords for body styles
        self.body_style_keywords = {
            'suv': ['suv', 'sport utility', 'crossover', 'cuv'],
            'truck': ['truck', 'pickup', 'pick-up', 'crew cab', 'extended cab', 'regular cab'],
            'sedan': ['sedan', 'saloon', '4-door', '4 door', 'four door'],
            'hatchback': ['hatchback', 'hatch', '5-door', '5 door', 'five door'],
            'convertible': ['convertible', 'roadster', 'cabriolet', 'cabrio', 'spider', 'spyder', 'drop top', 'soft top', 'hard top convertible'],
            'coupe': ['coupe', '2-door', '2 door', 'two door'],
            'van': ['van', 'minivan', 'mini-van', 'cargo van', 'passenger van'],
            'wagon': ['wagon', 'estate', 'touring', 'avant', 'sports tourer', 'shooting brake']
        }
        
        # Transmission patterns
        self.transmission_patterns = {
            'manual': [
                r'\b(manual|stick|standard|mt|5-speed|6-speed|5 speed|6 speed)\b',
                r'\b(5|6)\s*spd\b',
                r'\b(5|6)\s*speed\s*manual\b'
            ],
            'automatic': [
                r'\b(automatic|auto|at|cvt|dsg|dct|pdk|tiptronic|steptronic)\b',
                r'\b(7|8|9|10)\s*speed\b',
                r'\b(7|8|9|10)\s*spd\b'
            ]
        }
        
        # Fuel type patterns
        self.fuel_patterns = {
            'electric': [r'\b(electric|ev|battery|bev|tesla)\b', r'\bzero\s*emission\b'],
            'hybrid': [r'\b(hybrid|phev|plug-in|plugin)\b', r'\b(prius|insight|ioniq)\b'],
            'diesel': [r'\b(diesel|tdi|cdi|tdci|dci|hdi)\b'],
            'gasoline': [r'\b(gas|gasoline|petrol|unleaded)\b', r'\bv6\b', r'\bv8\b', r'\bturbo\b']
        }
        
        # Drivetrain patterns
        self.drivetrain_patterns = {
            'awd': [r'\b(awd|all wheel drive|all-wheel drive|4matic|xdrive|quattro|sh-awd)\b'],
            '4wd': [r'\b(4wd|4x4|four wheel drive|4 wheel drive)\b'],
            'fwd': [r'\b(fwd|front wheel drive|front-wheel drive|ff)\b'],
            'rwd': [r'\b(rwd|rear wheel drive|rear-wheel drive|fr)\b']
        }
        
        # Color extraction patterns (for title/description)
        self.color_patterns = {
            'black': [r'\b(black|ebony|onyx|midnight|carbon|jet)\b'],
            'white': [r'\b(white|pearl|snow|ivory|arctic|alabaster)\b'],
            'silver': [r'\b(silver|gray|grey|metallic|titanium|gunmetal)\b'],
            'red': [r'\b(red|crimson|burgundy|maroon|ruby|cardinal|cherry)\b'],
            'blue': [r'\b(blue|navy|azure|cobalt|sapphire|royal|sky)\b'],
            'green': [r'\b(green|emerald|forest|lime|mint|jade|olive)\b'],
            'brown': [r'\b(brown|tan|beige|mocha|chocolate|bronze|copper)\b'],
            'yellow': [r'\b(yellow|gold|golden|amber|mustard)\b'],
            'orange': [r'\b(orange|tangerine|rust)\b'],
            'purple': [r'\b(purple|violet|plum|lavender|magenta)\b']
        }

    def infer_attributes(self, vehicle_data: Dict[str, Any], source: str = 'ebay') -> Dict[str, Optional[str]]:
        """
        Infer vehicle attributes from various data fields.
        
        Args:
            vehicle_data: Raw vehicle data from the source
            source: The data source (ebay, carmax, etc.)
            
        Returns:
            Dictionary of inferred attributes
        """
        inferred = {
            'body_style': None,
            'transmission': None,
            'fuel_type': None,
            'drivetrain': None,
            'exterior_color': None,
            'engine': None
        }
        
        # Get text fields to analyze
        title = str(vehicle_data.get('title', '')).lower()
        model = str(vehicle_data.get('model', '')).lower()
        description = str(vehicle_data.get('description', '')).lower()
        
        # Source-specific field extraction
        if source == 'ebay':
            # eBay specific fields
            item_specifics = vehicle_data.get('item_specifics', {})
            if isinstance(item_specifics, dict):
                # Direct field mappings for eBay
                inferred['transmission'] = item_specifics.get('Transmission', inferred['transmission'])
                inferred['fuel_type'] = item_specifics.get('Fuel Type', inferred['fuel_type'])
                inferred['drivetrain'] = item_specifics.get('Drive Type', inferred['drivetrain'])
                inferred['exterior_color'] = item_specifics.get('Exterior Color', inferred['exterior_color'])
                inferred['body_style'] = item_specifics.get('Body Type', inferred['body_style'])
                
        elif source == 'carmax':
            # CarMax specific field mappings
            inferred['transmission'] = vehicle_data.get('transmissionType', inferred['transmission'])
            inferred['fuel_type'] = vehicle_data.get('fuelType', inferred['fuel_type'])
            inferred['drivetrain'] = vehicle_data.get('driveType', inferred['drivetrain'])
            inferred['exterior_color'] = vehicle_data.get('exteriorColor', inferred['exterior_color'])
            inferred['body_style'] = vehicle_data.get('bodyStyle', inferred['body_style'])
            
        elif source == 'cargurus':
            # CarGurus specific field mappings
            inferred['transmission'] = vehicle_data.get('transmission', inferred['transmission'])
            inferred['fuel_type'] = vehicle_data.get('fuelType', inferred['fuel_type'])
            inferred['drivetrain'] = vehicle_data.get('drivetrain', inferred['drivetrain'])
            inferred['exterior_color'] = vehicle_data.get('exteriorColor', inferred['exterior_color'])
            inferred['body_style'] = vehicle_data.get('bodyType', inferred['body_style'])
        
        # If attributes not found in structured data, infer from text
        combined_text = f"{title} {model} {description}"
        
        # Infer body style
        if not inferred['body_style']:
            inferred['body_style'] = self._infer_body_style(model, combined_text)
        
        # Infer transmission
        if not inferred['transmission']:
            inferred['transmission'] = self._infer_from_patterns(combined_text, self.transmission_patterns)
        
        # Infer fuel type
        if not inferred['fuel_type']:
            inferred['fuel_type'] = self._infer_from_patterns(combined_text, self.fuel_patterns)
            # Default to gasoline if not specified and not electric/hybrid
            if not inferred['fuel_type'] and not any(term in combined_text for term in ['electric', 'hybrid', 'ev']):
                inferred['fuel_type'] = 'gasoline'
        
        # Infer drivetrain
        if not inferred['drivetrain']:
            inferred['drivetrain'] = self._infer_from_patterns(combined_text, self.drivetrain_patterns)
        
        # Infer color
        if not inferred['exterior_color']:
            inferred['exterior_color'] = self._infer_from_patterns(combined_text, self.color_patterns)
        
        # Clean up values
        for key, value in inferred.items():
            if value:
                inferred[key] = value.lower().strip()
        
        return inferred
    
    def _infer_body_style(self, model: str, text: str) -> Optional[str]:
        """Infer body style from model name and text."""
        # First check model name mapping
        for body_style, models in self.model_body_style_map.items():
            for model_pattern in models:
                if model_pattern in model:
                    return body_style
        
        # Then check keywords in full text
        for body_style, keywords in self.body_style_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return body_style
        
        return None
    
    def _infer_from_patterns(self, text: str, patterns: Dict[str, List[str]]) -> Optional[str]:
        """Infer attribute from regex patterns."""
        for attr_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    return attr_type
        return None


# Example usage and testing
if __name__ == "__main__":
    inferencer = VehicleAttributeInferencer()
    
    # Test with sample eBay data
    test_data = {
        'title': '2019 Honda CR-V EX AWD Automatic',
        'model': 'CR-V',
        'item_specifics': {
            'Transmission': 'Automatic',
            'Drive Type': 'AWD'
        }
    }
    
    result = inferencer.infer_attributes(test_data, 'ebay')
    print(f"Inferred attributes: {result}")
    # Should output: body_style='suv', transmission='automatic', drivetrain='awd'