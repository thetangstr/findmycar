from sqlalchemy.orm import Session
from database import Vehicle
from ebay_client_improved import search_ebay_listings, get_item_details, EbayAPIError, RateLimitError
from cars_client import search_cars_listings
from autodev_client import AutoDevClient
from valuation import valuation_service
from ai_questions import question_generator
import re
import datetime
import logging

logger = logging.getLogger(__name__)

def get_aspect_value(aspects, name):
    """
    Extract aspect value from eBay Browse API aspects array.
    """
    if not aspects:
        return None
    
    for aspect in aspects:
        if aspect.get('name', '').lower() == name.lower():
            values = aspect.get('values', [])
            return values[0] if values else None
    return None

def extract_vehicle_info_from_title(title):
    """
    Enhanced vehicle information extraction from eBay listing titles.
    """
    if not title:
        return {}
    
    title_upper = title.upper()
    result = {}
    
    # Comprehensive make mapping
    make_patterns = {
        'HONDA': ['HONDA'],
        'TOYOTA': ['TOYOTA'],
        'FORD': ['FORD'],
        'CHEVROLET': ['CHEVROLET', 'CHEVY'],
        'BMW': ['BMW'],
        'MERCEDES': ['MERCEDES', 'MERCEDES-BENZ', 'BENZ'],
        'AUDI': ['AUDI'],
        'NISSAN': ['NISSAN'],
        'HYUNDAI': ['HYUNDAI'],
        'KIA': ['KIA'],
        'SUBARU': ['SUBARU'],
        'MAZDA': ['MAZDA'],
        'MITSUBISHI': ['MITSUBISHI'],
        'LEXUS': ['LEXUS'],
        'INFINITI': ['INFINITI'],
        'ACURA': ['ACURA'],
        'VOLKSWAGEN': ['VOLKSWAGEN', 'VW'],
        'PORSCHE': ['PORSCHE'],
        'TESLA': ['TESLA'],
        'VOLVO': ['VOLVO'],
        'JEEP': ['JEEP'],
        'DODGE': ['DODGE'],
        'CHRYSLER': ['CHRYSLER'],
        'BUICK': ['BUICK'],
        'CADILLAC': ['CADILLAC'],
        'GMC': ['GMC'],
        'LINCOLN': ['LINCOLN'],
        'LAND ROVER': ['LAND ROVER', 'LANDROVER'],
        'JAGUAR': ['JAGUAR'],
        'MINI': ['MINI'],
        'FIAT': ['FIAT'],
        'ALFA ROMEO': ['ALFA ROMEO', 'ALFA'],
        'MASERATI': ['MASERATI'],
        'FERRARI': ['FERRARI'],
        'LAMBORGHINI': ['LAMBORGHINI'],
        'BENTLEY': ['BENTLEY'],
        'ROLLS ROYCE': ['ROLLS ROYCE', 'ROLLS-ROYCE'],
        'MCLAREN': ['MCLAREN']
    }
    
    # Find make
    for make, patterns in make_patterns.items():
        for pattern in patterns:
            if pattern in title_upper:
                result['make'] = make.title()
                break
        if 'make' in result:
            break
    
    # Model extraction patterns for popular makes
    model_patterns = {
        'HONDA': ['CIVIC', 'ACCORD', 'CR-V', 'PILOT', 'ODYSSEY', 'FIT', 'RIDGELINE', 'PASSPORT', 'INSIGHT', 'HR-V'],
        'TOYOTA': ['CAMRY', 'COROLLA', 'RAV4', 'HIGHLANDER', 'PRIUS', 'SIENNA', 'TACOMA', 'TUNDRA', 'AVALON', 'C-HR'],
        'FORD': ['F-150', 'MUSTANG', 'EXPLORER', 'ESCAPE', 'FOCUS', 'FUSION', 'RANGER', 'EDGE', 'EXPEDITION', 'FIESTA'],
        'CHEVROLET': ['SILVERADO', 'EQUINOX', 'MALIBU', 'TRAVERSE', 'TAHOE', 'CAMARO', 'CRUZE', 'COLORADO', 'IMPALA', 'SUBURBAN'],
        'BMW': ['3 SERIES', '5 SERIES', 'X3', 'X5', 'X1', '7 SERIES', 'Z4', 'I3', 'I8', '4 SERIES', 'X7'],
        'TESLA': ['MODEL S', 'MODEL 3', 'MODEL X', 'MODEL Y', 'ROADSTER', 'CYBERTRUCK'],
        'NISSAN': ['ALTIMA', 'SENTRA', 'ROGUE', 'PATHFINDER', 'TITAN', 'FRONTIER', 'MURANO', 'VERSA', 'MAXIMA', 'ARMADA']
    }
    
    if 'make' in result:
        make_upper = result['make'].upper()
        if make_upper in model_patterns:
            for model in model_patterns[make_upper]:
                if model in title_upper:
                    result['model'] = model.title()
                    break
    
    # Extract year
    year_match = re.search(r'\b(19[9][0-9]|20[0-3][0-9])\b', title)
    if year_match:
        result['year'] = int(year_match.group(1))
    
    # Extract mileage from title
    mileage_patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*(?:miles?|mi\.?|k\s*miles?)',
        r'(\d{1,3})k\s*(?:miles?|mi\.?)',
        r'mileage:?\s*(\d{1,3}(?:,\d{3})*)',
        r'(\d{1,3}(?:,\d{3})*)\s*mile'
    ]
    
    for pattern in mileage_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            mileage_str = match.group(1).replace(',', '')
            try:
                mileage = int(mileage_str)
                # Handle 'k' notation
                if 'k' in match.group(0).lower():
                    mileage *= 1000
                if mileage < 500000:  # Reasonable upper limit
                    result['mileage'] = mileage
                    break
            except ValueError:
                continue
    
    return result

def parse_price(price_obj):
    """
    Parse price from eBay Browse API price object.
    """
    if isinstance(price_obj, dict):
        return float(price_obj.get('value', 0))
    elif isinstance(price_obj, str):
        return float(re.sub(r'[^\d.]', '', price_obj))
    return None

def extract_location(item):
    """
    Enhanced location extraction from eBay Browse API item.
    """
    if 'itemLocation' in item:
        location = item['itemLocation']
        city = location.get('city', '')
        state = location.get('stateOrProvince', '')
        country = location.get('country', '')
        postal_code = location.get('postalCode', '')
        
        # Build location string
        parts = []
        if city:
            parts.append(city)
        if state:
            parts.append(state)
        elif postal_code and country == 'US':
            # For US, try to extract state from postal code pattern
            if len(postal_code) >= 2:
                state_code = postal_code[:2]
                parts.append(state_code)
        
        if country and country != 'US':
            parts.append(country)
        
        return ', '.join(parts) if parts else 'Unknown'
    return 'Unknown'

def ingest_autodev_data(db: Session, query: str, filters=None, limit=50):
    """
    Ingest vehicle listings from Auto.dev
    """
    try:
        logger.info(f"Starting Auto.dev ingestion with query: {query}")
        
        # Initialize Auto.dev client
        autodev_client = AutoDevClient()
        
        # Search for vehicles
        search_result = autodev_client.search_vehicles(query, filters, limit=limit)
        
        if not search_result['success']:
            logger.error(f"Auto.dev search failed: {search_result.get('error')}")
            return {
                'success': False,
                'error': search_result.get('error'),
                'source': 'auto.dev'
            }
        
        vehicles = search_result['vehicles']
        logger.info(f"Found {len(vehicles)} Auto.dev listings")
        
        ingested_count = 0
        skipped_count = 0
        error_count = 0
        
        for vehicle_data in vehicles:
            try:
                external_id = vehicle_data.get('external_id')
                if not external_id:
                    error_count += 1
                    continue
                
                # Check if already exists (using external_id + source combination)
                db_vehicle = db.query(Vehicle).filter(
                    Vehicle.listing_id == external_id,
                    Vehicle.source == 'auto.dev'
                ).first()
                
                if db_vehicle:
                    skipped_count += 1
                    continue
                
                # Extract data from Auto.dev format
                make = vehicle_data.get('make')
                model = vehicle_data.get('model')
                year = vehicle_data.get('year')
                mileage = vehicle_data.get('mileage')
                condition = vehicle_data.get('condition', 'Used')
                listing_price = vehicle_data.get('price')
                
                # Get vehicle valuation if we have enough data
                valuation_data = {}
                if make and model and year and listing_price:
                    try:
                        valuation = valuation_service.get_vehicle_valuation(
                            make=make,
                            model=model,
                            year=year,
                            mileage=mileage,
                            condition=condition
                        )
                        
                        if valuation.get('estimated_value'):
                            deal_rating = valuation_service.calculate_deal_rating(
                                listing_price=listing_price,
                                estimated_value=valuation['estimated_value'],
                                market_min=valuation['market_min'],
                                market_max=valuation['market_max']
                            )
                            
                            valuation_data = {
                                'estimated_value': valuation['estimated_value'],
                                'market_min': valuation['market_min'],
                                'market_max': valuation['market_max'],
                                'deal_rating': deal_rating,
                                'valuation_confidence': valuation['confidence'],
                                'valuation_source': valuation['data_source'],
                                'last_valuation_update': datetime.datetime.utcnow()
                            }
                    except Exception as e:
                        logger.warning(f"Valuation failed for {make} {model} {year}: {e}")
                
                # Generate AI questions if possible
                buyer_questions = []
                try:
                    if make and model and year:
                        vehicle_context = {
                            'make': make,
                            'model': model,
                            'year': year,
                            'mileage': mileage,
                            'condition': condition,
                            'body_style': vehicle_data.get('body_style'),
                            'exterior_color': vehicle_data.get('exterior_color'),
                            'location': vehicle_data.get('location'),
                            'price': listing_price,
                            'title': vehicle_data.get('title'),
                            'dealer_name': vehicle_data.get('dealer_name'),
                            **valuation_data
                        }
                        
                        buyer_questions = question_generator.generate_buyer_questions(vehicle_context)
                except Exception as e:
                    logger.warning(f"Question generation failed for {make} {model} {year}: {e}")
                
                # Create vehicle record
                db_vehicle = Vehicle(
                    listing_id=external_id,
                    source='auto.dev',
                    title=vehicle_data.get('title'),
                    price=listing_price,
                    location=vehicle_data.get('location'),
                    image_urls=vehicle_data.get('image_urls', []),
                    view_item_url=vehicle_data.get('view_item_url'),
                    make=make,
                    model=model,
                    year=year,
                    mileage=mileage,
                    trim=vehicle_data.get('trim'),
                    condition=condition,
                    body_style=vehicle_data.get('body_style'),
                    exterior_color=vehicle_data.get('exterior_color'),
                    vin=vehicle_data.get('vin'),
                    vehicle_details=vehicle_data,  # Store full Auto.dev data
                    buyer_questions=buyer_questions,
                    **valuation_data
                )
                
                db.add(db_vehicle)
                db.commit()
                db.refresh(db_vehicle)
                ingested_count += 1
                
            except Exception as e:
                logger.error(f"Error processing Auto.dev listing {vehicle_data.get('external_id')}: {e}")
                error_count += 1
                continue
        
        logger.info(f"Auto.dev ingestion complete: {ingested_count} ingested, {skipped_count} skipped, {error_count} errors")
        
        return {
            'success': True,
            'ingested': ingested_count,
            'skipped': skipped_count,
            'errors': error_count,
            'total_available': search_result.get('total_available', len(vehicles)),
            'source': 'auto.dev'
        }
        
    except Exception as e:
        logger.error(f"Unexpected error during Auto.dev ingestion: {e}")
        return {
            'success': False,
            'error': f'Auto.dev ingestion error: {str(e)}',
            'source': 'auto.dev'
        }

def ingest_cars_data(db: Session, query: str, filters=None, limit=50):
    """
    Ingest vehicle listings from Cars.com
    """
    try:
        logger.info(f"Starting Cars.com ingestion with query: {query}")
        cars_listings = search_cars_listings(query, filters, limit=limit)
        
        logger.info(f"Found {len(cars_listings)} Cars.com listings")
        
        ingested_count = 0
        skipped_count = 0
        error_count = 0
        
        for item in cars_listings:
            try:
                listing_id = item.get('listing_id')
                if not listing_id:
                    error_count += 1
                    continue
                
                # Check if already exists
                db_vehicle = db.query(Vehicle).filter(Vehicle.listing_id == listing_id).first()
                if db_vehicle:
                    skipped_count += 1
                    continue
                
                # Extract data from Cars.com format
                make = item.get('make')
                model = item.get('model')
                year = item.get('year')
                mileage = item.get('mileage')
                condition = item.get('condition', 'Used')
                listing_price = item.get('price')
                
                # Get vehicle valuation if we have enough data
                valuation_data = {}
                if make and model and year and listing_price:
                    try:
                        valuation = valuation_service.get_vehicle_valuation(
                            make=make,
                            model=model,
                            year=year,
                            mileage=mileage,
                            condition=condition
                        )
                        
                        if valuation.get('estimated_value'):
                            deal_rating = valuation_service.calculate_deal_rating(
                                listing_price=listing_price,
                                estimated_value=valuation['estimated_value'],
                                market_min=valuation['market_min'],
                                market_max=valuation['market_max']
                            )
                            
                            valuation_data = {
                                'estimated_value': valuation['estimated_value'],
                                'market_min': valuation['market_min'],
                                'market_max': valuation['market_max'],
                                'deal_rating': deal_rating,
                                'valuation_confidence': valuation['confidence'],
                                'valuation_source': valuation['data_source'],
                                'last_valuation_update': datetime.datetime.utcnow()
                            }
                    except Exception as e:
                        logger.warning(f"Valuation failed for {make} {model} {year}: {e}")
                
                # Create vehicle record
                db_vehicle = Vehicle(
                    listing_id=listing_id,
                    source='cars.com',
                    title=item.get('title'),
                    price=listing_price,
                    location=item.get('location'),
                    image_urls=item.get('image_urls', []),
                    view_item_url=item.get('view_item_url'),
                    make=make,
                    model=model,
                    year=year,
                    mileage=mileage,
                    condition=condition,
                    vehicle_details=item.get('vehicle_details', {}),
                    buyer_questions=[],  # TODO: Generate questions
                    **valuation_data
                )
                
                db.add(db_vehicle)
                db.commit()
                db.refresh(db_vehicle)
                ingested_count += 1
                
            except Exception as e:
                logger.error(f"Error processing Cars.com listing {item.get('listing_id')}: {e}")
                error_count += 1
                continue
        
        logger.info(f"Cars.com ingestion complete: {ingested_count} ingested, {skipped_count} skipped, {error_count} errors")
        
        return {
            'success': True,
            'ingested': ingested_count,
            'skipped': skipped_count,
            'errors': error_count,
            'total_available': len(cars_listings),
            'source': 'cars.com'
        }
        
    except Exception as e:
        logger.error(f"Unexpected error during Cars.com ingestion: {e}")
        return {
            'success': False,
            'error': f'Cars.com ingestion error: {str(e)}',
            'source': 'cars.com'
        }

def ingest_multi_source_data(db: Session, query: str, filters=None, sources=['ebay', 'auto.dev']):
    """
    Ingest vehicle listings from multiple sources
    """
    results = {}
    total_ingested = 0
    total_skipped = 0
    total_errors = 0
    
    for source in sources:
        try:
            if source == 'ebay':
                result = ingest_data(db, query, filters)
            elif source == 'cars.com':
                result = ingest_cars_data(db, query, filters)
            elif source == 'auto.dev':
                result = ingest_autodev_data(db, query, filters)
            else:
                logger.warning(f"Unknown source: {source}")
                continue
                
            results[source] = result
            if result['success']:
                total_ingested += result['ingested']
                total_skipped += result['skipped']
                total_errors += result['errors']
                
        except Exception as e:
            logger.error(f"Error ingesting from {source}: {e}")
            results[source] = {
                'success': False,
                'error': str(e),
                'source': source
            }
    
    return {
        'success': len([r for r in results.values() if r['success']]) > 0,
        'results': results,
        'total_ingested': total_ingested,
        'total_skipped': total_skipped,
        'total_errors': total_errors
    }

def ingest_data(db: Session, query: str = "electric car", filters=None):
    """
    Ingests car listings from eBay into the database using Browse API.
    
    Returns:
        Dict with ingestion results including count and any errors
    """
    try:
        logger.info(f"Starting data ingestion with query: {query}")
        result = search_ebay_listings(query, filters, limit=100)
        items = result.get('items', [])
        total_available = result.get('total', 0)
        
        logger.info(f"Found {total_available} total items, processing {len(items)}")
        
        ingested_count = 0
        skipped_count = 0
        error_count = 0
        
        for item in items:
            listing_id = item.get("itemId")
            if not listing_id:
                error_count += 1
                continue
                
            db_vehicle = db.query(Vehicle).filter(Vehicle.listing_id == listing_id).first()

            if db_vehicle:
                skipped_count += 1
                continue

            try:
                # Skip detailed API calls for now to speed up ingestion
                # detailed_item = get_item_details(listing_id)
                # aspects = detailed_item.get('localizedAspects', []) if detailed_item else []
                aspects = []
            
                # Extract images
                image_urls = []
                if 'image' in item:
                    image_urls.append(item['image']['imageUrl'])
                if 'additionalImages' in item:
                    for img in item['additionalImages']:
                        image_urls.append(img['imageUrl'])

                # Extract vehicle details from title and available data
                title = item.get('title', '')
                
                # Try to extract make, model, year from title using enhanced parsing
                make = get_aspect_value(aspects, 'Make')
                model = get_aspect_value(aspects, 'Model') 
                year = int(get_aspect_value(aspects, 'Year')) if get_aspect_value(aspects, 'Year') else None
                
                # Enhanced make/model extraction from title
                parsed_vehicle = extract_vehicle_info_from_title(title)
                
                # Use parsed data if aspects don't have info
                if not make:
                    make = parsed_vehicle.get('make')
                if not model:
                    model = parsed_vehicle.get('model')
                if not year:
                    year = parsed_vehicle.get('year')
                
                # Extract mileage from aspects or title
                mileage = None
                aspect_mileage = get_aspect_value(aspects, 'Mileage')
                if aspect_mileage:
                    mileage = int(re.sub(r'[^\d]', '', aspect_mileage))
                elif 'mileage' in parsed_vehicle:
                    mileage = parsed_vehicle['mileage']
                condition = item.get('condition', 'good')
                trim = get_aspect_value(aspects, 'Trim')
                listing_price = parse_price(item.get("price"))
            
                # Get vehicle valuation if we have enough data
                valuation_data = {}
                if make and model and year and listing_price:
                    try:
                        valuation = valuation_service.get_vehicle_valuation(
                            make=make,
                            model=model, 
                            year=year,
                            mileage=mileage,
                            trim=trim,
                            condition=condition
                        )
                        
                        if valuation.get('estimated_value'):
                            # Calculate deal rating based on listing price
                            deal_rating = valuation_service.calculate_deal_rating(
                                listing_price=listing_price,
                                estimated_value=valuation['estimated_value'],
                                market_min=valuation['market_min'],
                                market_max=valuation['market_max']
                            )
                            
                            valuation_data = {
                                'estimated_value': valuation['estimated_value'],
                                'market_min': valuation['market_min'],
                                'market_max': valuation['market_max'],
                                'deal_rating': deal_rating,
                                'valuation_confidence': valuation['confidence'],
                                'valuation_source': valuation['data_source'],
                                'last_valuation_update': datetime.datetime.utcnow()
                            }
                    except Exception as e:
                        logger.warning(f"Valuation failed for {make} {model} {year}: {e}")

                # Generate AI questions (disabled for now to focus on core functionality)
                buyer_questions = []
                # TODO: Re-enable question generation after fixing None handling
                # try:
                #     vehicle_context = {
                #         'make': make,
                #         'model': model,
                #         'year': year,
                #         'mileage': mileage,
                #         'condition': condition,
                #         'transmission': get_aspect_value(aspects, 'Transmission'),
                #         'fuel_type': get_aspect_value(aspects, 'Fuel Type'),
                #         'body_style': get_aspect_value(aspects, 'Body Type'),
                #         'location': extract_location(item),
                #         'price': listing_price,
                #         'title': item.get("title"),
                #         **valuation_data  # Include valuation data if available
                #     }
                #     
                #     buyer_questions = question_generator.generate_buyer_questions(vehicle_context)
                # except Exception as e:
                #     logger.warning(f"Question generation failed for {make} {model} {year}: {e}")

                vehicle = Vehicle(
                    listing_id=listing_id,
                    title=item.get("title"),
                    price=listing_price,
                    location=extract_location(item),
                    image_urls=image_urls,
                    view_item_url=item.get('itemWebUrl'),
                    make=make,
                    model=model,
                    year=year,
                    mileage=mileage,
                    trim=trim,
                    condition=condition,
                    body_style=get_aspect_value(aspects, 'Body Type'),
                    transmission=get_aspect_value(aspects, 'Transmission'),
                    drivetrain=get_aspect_value(aspects, 'Drive Type'),
                    fuel_type=get_aspect_value(aspects, 'Fuel Type'),
                    exterior_color=get_aspect_value(aspects, 'Exterior Color'),
                    interior_color=get_aspect_value(aspects, 'Interior Color'),
                    vin=get_aspect_value(aspects, 'Vehicle Identification Number (VIN)'),
                    vehicle_details=item,  # Store raw item data
                    buyer_questions=buyer_questions,  # AI-generated questions
                    **valuation_data  # Add valuation fields
                )
                db.add(vehicle)
                ingested_count += 1
                
            except EbayAPIError as e:
                logger.error(f"eBay API error for item {listing_id}: {e}")
                error_count += 1
            except Exception as e:
                logger.error(f"Unexpected error processing item {listing_id}: {e}")
                error_count += 1
                
        db.commit()
        
        logger.info(f"Ingestion complete: {ingested_count} added, {skipped_count} skipped, {error_count} errors")
        
        return {
            'success': True,
            'ingested': ingested_count,
            'skipped': skipped_count,
            'errors': error_count,
            'total_available': total_available
        }
        
    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {e}")
        return {
            'success': False,
            'error': 'Rate limit exceeded. Please try again later.',
            'retry_after': e.response_data.get('retry_after')
        }
    except EbayAPIError as e:
        logger.error(f"eBay API error: {e}")
        return {
            'success': False,
            'error': f'eBay API error: {str(e)}'
        }
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {e}")
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

