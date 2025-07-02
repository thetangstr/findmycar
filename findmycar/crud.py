from sqlalchemy.orm import Session
from sqlalchemy import case
from database import Vehicle
import schemas

def get_vehicle(db: Session, vehicle_id: int):
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def get_vehicles(db: Session, skip: int = 0, limit: int = 100, sort_by: str = "newest"):
    query = db.query(Vehicle)
    
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

def get_vehicle_count(db: Session):
    return db.query(Vehicle).count()

def create_vehicle(db: Session, vehicle: schemas.Vehicle):
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle