from sqlalchemy.orm import Session
from sqlalchemy import case, or_, not_
from database import Vehicle
import schemas

def get_vehicle(db: Session, vehicle_id: int):
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def get_vehicles(db: Session, skip: int = 0, limit: int = 100, sort_by: str = "newest", filters: dict = None):
    query = db.query(Vehicle)
    
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 get_vehicles called with filters: {filters}")
    
    # Apply filters if provided
    if filters:
        if filters.get('make'):
            query = query.filter(Vehicle.make.ilike(f"%{filters['make']}%"))
        if filters.get('model'):
            query = query.filter(Vehicle.model.ilike(f"%{filters['model']}%"))
        if filters.get('year_min'):
            query = query.filter(Vehicle.year >= filters['year_min'])
        if filters.get('year_max'):
            query = query.filter(Vehicle.year <= filters['year_max'])
        if filters.get('price_min'):
            query = query.filter(Vehicle.price >= filters['price_min'])
        if filters.get('price_max'):
            query = query.filter(Vehicle.price <= filters['price_max'])
        if filters.get('mileage_min'):
            query = query.filter(Vehicle.mileage >= filters['mileage_min'])
        if filters.get('mileage_max'):
            query = query.filter(Vehicle.mileage <= filters['mileage_max'])
        if filters.get('body_style'):
            query = query.filter(Vehicle.body_style.ilike(f"%{filters['body_style']}%"))
        if filters.get('exterior_color'):
            query = query.filter(Vehicle.exterior_color.ilike(f"%{filters['exterior_color']}%"))
        if filters.get('exclude_colors'):
            logger.info(f"🎨 Applying exclude_colors filter: {filters['exclude_colors']}")
            for color in filters['exclude_colors']:
                # Exclude vehicles that have this color, but include vehicles with no color
                logger.info(f"  Excluding color: {color}")
                query = query.filter(
                    or_(
                        Vehicle.exterior_color == None,
                        Vehicle.exterior_color == '',
                        ~Vehicle.exterior_color.ilike(f"%{color}%")
                    )
                )
        if filters.get('transmission'):
            query = query.filter(Vehicle.transmission.ilike(f"%{filters['transmission']}%"))
        if filters.get('fuel_type'):
            query = query.filter(Vehicle.fuel_type.ilike(f"%{filters['fuel_type']}%"))
        if filters.get('drivetrain'):
            query = query.filter(Vehicle.drivetrain.ilike(f"%{filters['drivetrain']}%"))
        if filters.get('trim'):
            query = query.filter(Vehicle.trim.ilike(f"%{filters['trim']}%"))
    
    # Apply sorting
    if sort_by == "newest":
        query = query.order_by(Vehicle.created_at.desc())
    elif sort_by == "oldest":
        query = query.order_by(Vehicle.created_at.asc())
    elif sort_by == "price_low":
        query = query.order_by(Vehicle.price.asc())
    elif sort_by == "price_high":
        query = query.order_by(Vehicle.price.desc())
    elif sort_by == "mileage_low":
        query = query.order_by(Vehicle.mileage.asc())
    elif sort_by == "mileage_high":
        query = query.order_by(Vehicle.mileage.desc())
    elif sort_by == "year_new":
        query = query.order_by(Vehicle.year.desc())
    elif sort_by == "year_old":
        query = query.order_by(Vehicle.year.asc())
    elif sort_by == "deal_best":
        # Sort by deal rating, with best deals first
        query = query.order_by(
            case(
                (Vehicle.deal_rating == "Great Deal", 1),
                (Vehicle.deal_rating == "Good Deal", 2),
                (Vehicle.deal_rating == "Fair Price", 3),
                (Vehicle.deal_rating == "High Price", 4),
                else_=5
            )
        )
    else:
        # Default to newest
        query = query.order_by(Vehicle.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

def get_vehicle_count(db: Session, filters: dict = None):
    query = db.query(Vehicle)
    
    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 get_vehicle_count called with filters: {filters}")
    
    # Apply filters if provided
    if filters:
        if filters.get('make'):
            query = query.filter(Vehicle.make.ilike(f"%{filters['make']}%"))
        if filters.get('model'):
            query = query.filter(Vehicle.model.ilike(f"%{filters['model']}%"))
        if filters.get('year_min'):
            query = query.filter(Vehicle.year >= filters['year_min'])
        if filters.get('year_max'):
            query = query.filter(Vehicle.year <= filters['year_max'])
        if filters.get('price_min'):
            query = query.filter(Vehicle.price >= filters['price_min'])
        if filters.get('price_max'):
            query = query.filter(Vehicle.price <= filters['price_max'])
        if filters.get('mileage_min'):
            query = query.filter(Vehicle.mileage >= filters['mileage_min'])
        if filters.get('mileage_max'):
            query = query.filter(Vehicle.mileage <= filters['mileage_max'])
        if filters.get('body_style'):
            query = query.filter(Vehicle.body_style.ilike(f"%{filters['body_style']}%"))
        if filters.get('exterior_color'):
            query = query.filter(Vehicle.exterior_color.ilike(f"%{filters['exterior_color']}%"))
        if filters.get('exclude_colors'):
            logger.info(f"🎨 Applying exclude_colors filter: {filters['exclude_colors']}")
            for color in filters['exclude_colors']:
                # Exclude vehicles that have this color, but include vehicles with no color
                logger.info(f"  Excluding color: {color}")
                query = query.filter(
                    or_(
                        Vehicle.exterior_color == None,
                        Vehicle.exterior_color == '',
                        ~Vehicle.exterior_color.ilike(f"%{color}%")
                    )
                )
        if filters.get('transmission'):
            query = query.filter(Vehicle.transmission.ilike(f"%{filters['transmission']}%"))
        if filters.get('fuel_type'):
            query = query.filter(Vehicle.fuel_type.ilike(f"%{filters['fuel_type']}%"))
        if filters.get('drivetrain'):
            query = query.filter(Vehicle.drivetrain.ilike(f"%{filters['drivetrain']}%"))
        if filters.get('trim'):
            query = query.filter(Vehicle.trim.ilike(f"%{filters['trim']}%"))
    
    return query.count()

def create_vehicle(db: Session, vehicle: schemas.Vehicle):
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle