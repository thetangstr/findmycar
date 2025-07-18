import re
import openai
from typing import Dict, Optional
from config import OPENAI_API_KEY
from chassis_codes import parse_chassis_code

def parse_natural_language_query(query: str) -> Dict[str, Optional[str]]:
    """
    Parse natural language search query into structured filters.
    Uses both rule-based parsing and AI assistance.
    """
    
    # Initialize filters
    filters = {
        'make': None,
        'model': None,
        'year_min': None,
        'year_max': None,
        'price_min': None,
        'price_max': None,
        'mileage_min': None,
        'mileage_max': None,
        'body_style': None,
        'fuel_type': None,
        'transmission': None,
        'exterior_color': None,
        'exclude_colors': [],
        'trim': None,
        'drivetrain': None,
        'sources': None,  # Add sources filter
        'parsed_query': query
    }
    
    # Check for chassis codes first (highest priority)
    chassis_info = parse_chassis_code(query)
    if chassis_info.get('found'):
        filters['make'] = chassis_info['make']
        filters['model'] = chassis_info['model']
        filters['year_min'] = chassis_info['year_min']
        filters['year_max'] = chassis_info['year_max']
        filters['chassis_code'] = chassis_info['chassis_code']
        filters['variant'] = chassis_info.get('variant', '')
        # Log the chassis code detection
        import logging
        logging.info(f"🎯 Chassis code detected: {chassis_info['chassis_code']} = {chassis_info['year_min']}-{chassis_info['year_max']} {chassis_info['make']} {chassis_info['model']} {chassis_info.get('variant', '')}")
    
    # Rule-based parsing for common patterns (don't override chassis code results)
    rule_based = _rule_based_parsing(query)
    for key, value in rule_based.items():
        # Special handling for lists like exclude_colors
        if key == 'exclude_colors' and isinstance(value, list):
            filters[key].extend(value)
        # Only update if not already set by chassis code
        elif filters.get(key) is None and value is not None:
            filters[key] = value
    
    # AI parsing is currently disabled due to outdated OpenAI API
    # TODO: Update to use new OpenAI API when needed
    # try:
    #     ai_filters = _ai_parsing(query)
    #     # Merge AI results, preferring existing results when available
    #     for key, value in ai_filters.items():
    #         if filters.get(key) is None and value is not None:
    #             filters[key] = value
    # except Exception as e:
    #     print(f"AI parsing failed, using rule-based only: {e}")
    
    return filters

def _rule_based_parsing(query: str) -> Dict[str, Optional[str]]:
    """
    Extract structured data from query using regex patterns.
    """
    filters = {
        'exclude_colors': []  # Initialize as empty list
    }
    query_lower = query.lower()
    
    # Extract source filters first (e.g., "source:ebay" or "from:cargurus")
    source_patterns = [
        r'source:(\w+)',
        r'from:(\w+)',
        r'on:(\w+)'
    ]
    
    detected_sources = []
    for pattern in source_patterns:
        matches = re.findall(pattern, query_lower)
        for match in matches:
            source = match.lower()
            # Map common variations to actual source names
            source_map = {
                'ebay': 'ebay',
                'carmax': 'carmax',
                'cargurus': 'cargurus',
                'bat': 'bringatrailer',
                'bringatrailer': 'bringatrailer',
                'truecar': 'truecar',
                'cars': 'cars.com',
                'carscom': 'cars.com',
                'cars.com': 'cars.com',
                'autodev': 'auto.dev',
                'auto.dev': 'auto.dev'
            }
            if source in source_map:
                detected_sources.append(source_map[source])
                # Remove the source syntax from query for further parsing
                query_lower = re.sub(f'{pattern}', '', query_lower)
    
    if detected_sources:
        filters['sources'] = list(set(detected_sources))  # Remove duplicates
    
    # Clean the query by removing source syntax
    cleaned_query = query
    for pattern in source_patterns:
        cleaned_query = re.sub(f'{pattern}', '', cleaned_query, flags=re.IGNORECASE)
    filters['cleaned_query'] = cleaned_query.strip()
    
    # Extract years first (only match realistic car years: 1990-2030)
    year_patterns = [
        r'(19[9][0-9]|20[0-3][0-9])\s*-\s*(19[9][0-9]|20[0-3][0-9])',
        r'between\s*(19[9][0-9]|20[0-3][0-9])\s*and\s*(19[9][0-9]|20[0-3][0-9])',
        r'(19[9][0-9]|20[0-3][0-9])\s*to\s*(19[9][0-9]|20[0-3][0-9])',
        r'after\s*(19[9][0-9]|20[0-3][0-9])',
        r'since\s*(19[9][0-9]|20[0-3][0-9])',
        r'newer than\s*(19[9][0-9]|20[0-3][0-9])',
        r'before\s*(19[9][0-9]|20[0-3][0-9])',
        r'older than\s*(19[9][0-9]|20[0-3][0-9])',
        r'\b(19[9][0-9]|20[0-3][0-9])\b',  # Single year with word boundaries
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, query)
        if match:
            if 'after' in pattern or 'since' in pattern or 'newer' in pattern:
                filters['year_min'] = int(match.group(1))
            elif 'before' in pattern or 'older' in pattern:
                filters['year_max'] = int(match.group(1))
            elif len(match.groups()) > 1 and match.group(2):  # Range
                filters['year_min'] = int(match.group(1))
                filters['year_max'] = int(match.group(2))
            else:  # Single year
                year = int(match.group(1))
                filters['year_min'] = year
                filters['year_max'] = year
            break
    
    # Extract price ranges (more specific to avoid year conflicts and mileage conflicts)
    price_patterns = [
        r'under\s*\$(\d+(?:,\d+)*(?:k|000)?)',  # Must have dollar sign
        r'below\s*\$(\d+(?:,\d+)*(?:k|000)?)',  # Must have dollar sign
        r'less than\s*\$(\d+(?:,\d+)*(?:k|000)?)',  # Must have dollar sign
        r'under\s+(\d+k)',  # Handle "under 40k" without dollar sign
        r'below\s+(\d+k)',  # Handle "below 40k" without dollar sign
        r'\$(\d+(?:,\d+)*(?:k|000)?)\s*-\s*\$(\d+(?:,\d+)*(?:k|000)?)',
        r'between\s*\$(\d+(?:,\d+)*(?:k|000)?)\s*and\s*\$(\d+(?:,\d+)*(?:k|000)?)',
        r'under\s*(\d+(?:,\d+)*(?:k|000)?)\s*(?:dollars?|bucks?)',  # Followed by money words
        r'below\s*(\d+(?:,\d+)*(?:k|000)?)\s*(?:dollars?|bucks?)',  # Followed by money words
        r'budget\s*(?:of\s*)?(\d+(?:,\d+)*(?:k|000)?)',
        r'price\s*(?:range\s*)?(?:under\s*)?(\d+(?:,\d+)*(?:k|000)?)',
        r'\$?(\d{4,}(?:,\d+)*(?:k|000)?)\s*-\s*\$?(\d{4,}(?:,\d+)*(?:k|000)?)',  # 4+ digits for prices
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, query_lower)
        if match:
            # Skip if this looks like a year range (4-digit numbers in 1990-2030 range)
            try:
                first_num = int(match.group(1).replace(',', '').replace('k', '000').replace('000', ''))
                if 1990 <= first_num <= 2030:
                    continue
                if match.group(2) if len(match.groups()) > 1 else None:
                    second_num = int(match.group(2).replace(',', '').replace('k', '000').replace('000', ''))
                    if 1990 <= second_num <= 2030:
                        continue
            except:
                pass
                
            if 'under' in pattern or 'below' in pattern or 'less than' in pattern:
                filters['price_max'] = _parse_price_value(match.group(1))
            else:
                filters['price_min'] = _parse_price_value(match.group(1))
                if len(match.groups()) > 1 and match.group(2):
                    filters['price_max'] = _parse_price_value(match.group(2))
            break
    
    # Extract mileage ranges (similar to price patterns)
    mileage_patterns = [
        r'under\s*(\d+(?:,\d+)*(?:k|000)?)\s*miles?',
        r'below\s*(\d+(?:,\d+)*(?:k|000)?)\s*miles?',
        r'less than\s*(\d+(?:,\d+)*(?:k|000)?)\s*miles?',
        r'(\d+(?:,\d+)*(?:k|000)?)\s*-\s*(\d+(?:,\d+)*(?:k|000)?)\s*miles?',
        r'between\s*(\d+(?:,\d+)*(?:k|000)?)\s*and\s*(\d+(?:,\d+)*(?:k|000)?)\s*miles?',
        r'(\d+(?:,\d+)*(?:k|000)?)\s*to\s*(\d+(?:,\d+)*(?:k|000)?)\s*miles?',
        r'max\s*(\d+(?:,\d+)*(?:k|000)?)\s*miles?',
        r'maximum\s*(\d+(?:,\d+)*(?:k|000)?)\s*miles?',
        r'high\s*mileage',  # Special case for high mileage
        r'low\s*mileage',   # Special case for low mileage
    ]
    
    for pattern in mileage_patterns:
        match = re.search(pattern, query_lower)
        if match:
            if 'high' in pattern and 'mileage' in pattern:
                filters['mileage_min'] = 100000  # Consider high mileage as 100k+
            elif 'low' in pattern and 'mileage' in pattern:
                filters['mileage_max'] = 50000   # Consider low mileage as under 50k
            elif 'under' in pattern or 'below' in pattern or 'less than' in pattern or 'max' in pattern:
                if match.groups():  # Check if there are groups
                    filters['mileage_max'] = _parse_mileage_value(match.group(1))
            else:
                if match.groups():  # Check if there are groups
                    filters['mileage_min'] = _parse_mileage_value(match.group(1))
                    if len(match.groups()) > 1 and match.group(2):
                        filters['mileage_max'] = _parse_mileage_value(match.group(2))
            break
    
    # Extract common makes and models
    makes_models = {
        'honda': ['civic', 'accord', 'cr-v', 'pilot', 'odyssey', 'fit', 'ridgeline', 'passport', 'insight'],
        'toyota': ['camry', 'corolla', 'rav4', 'highlander', 'prius', 'sienna', 'tacoma', 'tundra', 'avalon'],
        'ford': ['f-150', 'mustang', 'explorer', 'escape', 'focus', 'fusion', 'ranger', 'edge', 'expedition'],
        'chevrolet': ['silverado', 'equinox', 'malibu', 'traverse', 'tahoe', 'camaro', 'cruze', 'colorado'],
        'nissan': ['altima', 'sentra', 'rogue', 'pathfinder', 'titan', 'frontier', 'murano', 'versa'],
        'bmw': ['3 series', '5 series', 'x3', 'x5', 'x1', '7 series', 'z4', 'i3', 'i8'],
        'mercedes': ['c-class', 'e-class', 's-class', 'glc', 'gle', 'gls', 'a-class', 'cls'],
        'audi': ['a3', 'a4', 'a6', 'a8', 'q3', 'q5', 'q7', 'q8', 'tt'],
        'tesla': ['model s', 'model 3', 'model x', 'model y', 'roadster', 'cybertruck'],
        'subaru': ['outback', 'forester', 'impreza', 'legacy', 'crosstrek', 'ascent', 'wrx']
    }
    
    # Find make first
    detected_make = None
    for make in makes_models.keys():
        if make in query_lower or (make == 'chevrolet' and 'chevy' in query_lower):
            detected_make = make
            filters['make'] = make.title()
            if make == 'chevrolet' and 'chevy' in query_lower:
                filters['make'] = 'Chevrolet'
            break
    
    # Then find model if make was detected
    if detected_make and detected_make in makes_models:
        for model in makes_models[detected_make]:
            if model in query_lower:
                filters['model'] = model.title()
                break
    
    # Extract body styles
    body_styles = {
        'sedan': ['sedan', 'saloon'],
        'suv': ['suv', 'sport utility', 'crossover'],
        'truck': ['truck', 'pickup'],
        'convertible': ['convertible', 'cabriolet', 'roadster'],
        'coupe': ['coupe', 'coup'],
        'hatchback': ['hatchback', 'hatch'],
        'wagon': ['wagon', 'estate'],
        'van': ['van', 'minivan']
    }
    
    for style, keywords in body_styles.items():
        for keyword in keywords:
            if keyword in query_lower:
                filters['body_style'] = style
                break
        if filters.get('body_style'):
            break
    
    # Extract colors (including negative conditions)
    colors = {
        'black': ['black', 'ebony', 'onyx', 'midnight'],
        'white': ['white', 'pearl', 'snow', 'ivory'],
        'silver': ['silver', 'gray', 'grey', 'metallic'],
        'red': ['red', 'crimson', 'burgundy', 'maroon', 'ruby'],
        'blue': ['blue', 'navy', 'azure', 'cobalt', 'sapphire'],
        'green': ['green', 'emerald', 'forest', 'lime', 'mint'],
        'yellow': ['yellow', 'gold', 'golden', 'amber'],
        'orange': ['orange', 'copper', 'bronze'],
        'brown': ['brown', 'tan', 'beige', 'mocha', 'chocolate'],
        'purple': ['purple', 'violet', 'plum', 'lavender']
    }
    
    # Check for negative color conditions first
    exclude_patterns = [
        r'not\s+(\w+)',
        r'no\s+(\w+)',
        r'except\s+(\w+)',
        r'exclude\s+(\w+)',
        r'without\s+(\w+)'
    ]
    
    for pattern in exclude_patterns:
        matches = re.findall(pattern, query_lower)
        for match in matches:
            for color, keywords in colors.items():
                if match in keywords:
                    filters['exclude_colors'].append(color)
                    break
    
    # Then check for positive color preferences
    for color, keywords in colors.items():
        if color not in filters['exclude_colors']:  # Don't set if excluded
            for keyword in keywords:
                if keyword in query_lower and f'not {keyword}' not in query_lower and f'no {keyword}' not in query_lower:
                    filters['exterior_color'] = color
                    break
            if filters.get('exterior_color'):
                break
    
    # Extract fuel types
    fuel_types = {
        'electric': ['electric', 'ev', 'battery'],
        'hybrid': ['hybrid', 'prius'],
        'diesel': ['diesel', 'tdi'],
        'gasoline': ['gas', 'gasoline', 'petrol']
    }
    
    for fuel, keywords in fuel_types.items():
        for keyword in keywords:
            if keyword in query_lower:
                filters['fuel_type'] = fuel
                break
        if filters.get('fuel_type'):
            break
    
    # Extract transmission
    if any(word in query_lower for word in ['manual', 'stick', 'standard', '6-speed manual', '5-speed manual', '5 speed', '6 speed', 'mt']):
        filters['transmission'] = 'manual'
    elif any(word in query_lower for word in ['automatic', 'auto', 'cvt', 'at']):
        filters['transmission'] = 'automatic'
    
    # Extract drivetrain types
    drivetrain_types = {
        'awd': ['awd', 'all wheel drive', 'all-wheel drive', 'all wheel', '4matic', 'xdrive', 'quattro'],
        '4wd': ['4wd', '4x4', 'four wheel drive', '4 wheel drive'],
        'fwd': ['fwd', 'front wheel drive', 'front-wheel drive'],
        'rwd': ['rwd', 'rear wheel drive', 'rear-wheel drive']
    }
    
    for drivetrain, keywords in drivetrain_types.items():
        for keyword in keywords:
            if keyword in query_lower:
                filters['drivetrain'] = drivetrain
                break
        if filters.get('drivetrain'):
            break
    
    # Extract trim levels (common patterns)
    trim_patterns = [
        r'\b(base|sport|touring|limited|premium|luxury|executive|platinum)\b',
        r'\b(lx|ex|ex-l|si|type r|type s)\b',  # Honda trims
        r'\b(s|se|sel|ses|titanium)\b',  # Ford trims
        r'\b(ls|lt|ltz|premier|rs|ss|zl1)\b',  # Chevy trims
        r'\b(sr|sr5|trd|xle|xse|le)\b',  # Toyota trims
    ]
    
    for pattern in trim_patterns:
        match = re.search(pattern, query_lower)
        if match:
            filters['trim'] = match.group(1).upper()
            break
    
    return filters

def _parse_price_value(price_str: str) -> int:
    """
    Parse price string like '30k', '30,000', '30000' into integer.
    """
    price_str = price_str.replace(',', '').lower()
    if price_str.endswith('k'):
        return int(float(price_str[:-1]) * 1000)
    return int(price_str)

def _parse_mileage_value(mileage_str: str) -> int:
    """
    Parse mileage string like '100k', '100,000', '100000' into integer.
    """
    mileage_str = mileage_str.replace(',', '').lower()
    if mileage_str.endswith('k'):
        return int(float(mileage_str[:-1]) * 1000)
    return int(mileage_str)

def _ai_parsing(query: str) -> Dict[str, Optional[str]]:
    """
    Use OpenAI API to parse complex natural language queries.
    """
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key":
            return {}
            
        openai.api_key = OPENAI_API_KEY
        
        prompt = f"""
        Parse this car search query into structured filters. Return a JSON object with these fields:
        - make: car manufacturer (e.g., "Honda", "Toyota")
        - model: specific model (e.g., "Civic", "Camry") 
        - year_min: minimum year (integer)
        - year_max: maximum year (integer)
        - price_min: minimum price in dollars (integer)
        - price_max: maximum price in dollars (integer)
        - body_style: type (e.g., "sedan", "suv", "truck", "convertible")
        - fuel_type: fuel type (e.g., "electric", "hybrid", "diesel", "gasoline")
        - transmission: transmission type (e.g., "manual", "automatic")
        - use_case: intended use (e.g., "family", "commuting", "construction", "racing")
        
        Return only valid JSON with null for unknown fields.
        
        Query: "{query}"
        """
        
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=200,
            temperature=0.1
        )
        
        # Parse the JSON response
        import json
        result = json.loads(response.choices[0].text.strip())
        return result
        
    except Exception as e:
        print(f"OpenAI parsing error: {e}")
        return {}

def enhance_query_with_use_case(query: str, use_case: str = None) -> str:
    """
    Enhance search query based on use case requirements.
    """
    if not use_case:
        return query
    
    use_case_enhancements = {
        'construction': 'truck pickup heavy duty towing capacity payload',
        'family': 'suv sedan safety reliable spacious',
        'commuting': 'fuel efficient reliable sedan hybrid',
        'racing': 'sports car performance manual transmission',
        'luxury': 'premium leather navigation sunroof',
        'off-road': 'suv truck 4wd awd ground clearance'
    }
    
    if use_case.lower() in use_case_enhancements:
        additional_terms = use_case_enhancements[use_case.lower()]
        return f"{query} {additional_terms}"
    
    return query