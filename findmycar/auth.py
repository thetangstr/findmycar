"""
Simple authentication system for FindMyCar
Provides basic user management and session handling
"""
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base, SessionLocal
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import secrets
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = secrets.token_hex(32)  # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security scheme
security = HTTPBearer(auto_error=False)

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
class UserCreate:
    """User creation schema"""
    def __init__(self, email: str, username: str, password: str):
        self.email = email
        self.username = username
        self.password = password

class UserAuth:
    """User authentication schema"""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_create: UserCreate) -> User:
    """Create a new user"""
    # Check if user already exists
    existing_user = get_user_by_username(db, user_create.username)
    if existing_user:
        raise ValueError("Username already exists")
    
    existing_email = get_user_by_email(db, user_create.email)
    if existing_email:
        raise ValueError("Email already exists")
    
    # Create new user
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.email,
        username=user_create.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"New user created: {user_create.username}")
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"User authenticated: {username}")
    return user

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(lambda: SessionLocal())
) -> Optional[User]:
    """Get current authenticated user"""
    
    # Try JWT token first
    if credentials:
        token_data = verify_token(credentials.credentials)
        if token_data:
            username = token_data.get("sub")
            if username:
                user = get_user_by_username(db, username)
                if user and user.is_active:
                    return user
    
    # Fallback to session-based auth (for existing functionality)
    session_id = request.cookies.get("session_id")
    if session_id:
        # This integrates with existing session system
        from database import UserSession
        session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
        if session:
            # For now, treat all sessions as anonymous users
            # In a full implementation, you'd link sessions to users
            return None
    
    return None

def require_auth(current_user: User = Depends(get_current_user)) -> User:
    """Require authentication - raises 401 if not authenticated"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def require_admin(current_user: User = Depends(require_auth)) -> User:
    """Require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return current_user

def optional_auth(current_user: Optional[User] = Depends(get_current_user)) -> Optional[User]:
    """Optional authentication - doesn't raise error if not authenticated"""
    return current_user

# Rate limiting per user
def get_user_rate_limit_key(user: Optional[User], request: Request) -> str:
    """Get rate limiting key for user or IP"""
    if user:
        return f"user:{user.id}"
    else:
        return f"ip:{request.client.host}"

# Initialize auth tables
def init_auth_tables():
    """Create authentication tables"""
    try:
        from database import engine
        Base.metadata.create_all(bind=engine, tables=[User.__table__])
        logger.info("Authentication tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize auth tables: {e}")

# Create default admin user if none exists
def create_default_admin():
    """Create default admin user if no users exist"""
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            admin_user = UserCreate(
                email="admin@findmycar.com",
                username="admin",
                password="changeme123!"  # Should be changed immediately
            )
            user = create_user(db, admin_user)
            user.is_admin = True
            db.commit()
            
            logger.warning("Default admin user created - USERNAME: admin, PASSWORD: changeme123!")
            logger.warning("Please change the default password immediately!")
            
    except Exception as e:
        logger.error(f"Failed to create default admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Test authentication system
    init_auth_tables()
    create_default_admin()