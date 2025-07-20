#!/usr/bin/env python3
"""
Enhanced API authentication system for production
Supports API keys, JWT tokens, and rate limiting per user
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

from flask import request, jsonify, current_app
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Float, JSON
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext
import redis

from database_v2_sqlite import Base, get_session

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
API_KEY_LENGTH = 32

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class APIUser(Base):
    """API user model with enhanced features"""
    __tablename__ = "api_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # API access
    api_key = Column(String, unique=True, index=True)
    api_key_created_at = Column(DateTime)
    
    # Permissions
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    allowed_endpoints = Column(JSON, default=list)  # List of allowed endpoints
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    
    # Usage tracking
    total_requests = Column(Integer, default=0)
    last_request_at = Column(DateTime)
    monthly_usage = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APIKey(Base):
    """API key management"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    name = Column(String)  # Key description/name
    
    # Permissions
    is_active = Column(Boolean, default=True)
    scopes = Column(JSON, default=list)  # ['read', 'write', 'admin']
    allowed_origins = Column(JSON, default=list)  # CORS origins
    
    # Expiration
    expires_at = Column(DateTime)
    
    # Usage
    last_used_at = Column(DateTime)
    usage_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)

class AuthenticationManager:
    """Manages API authentication and authorization"""
    
    def __init__(self, db: Session, cache_client=None):
        self.db = db
        self.cache = cache_client
    
    def create_user(self, email: str, username: str, password: str, 
                   is_admin: bool = False) -> APIUser:
        """Create a new API user"""
        # Check if user exists
        existing = self.db.query(APIUser).filter(
            (APIUser.email == email) | (APIUser.username == username)
        ).first()
        
        if existing:
            raise ValueError("User already exists")
        
        # Create user
        user = APIUser(
            email=email,
            username=username,
            hashed_password=pwd_context.hash(password),
            is_admin=is_admin
        )
        
        # Generate initial API key
        api_key = self.generate_api_key()
        user.api_key = api_key
        user.api_key_created_at = datetime.utcnow()
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def generate_api_key(self) -> str:
        """Generate a secure API key"""
        return f"fmc_{secrets.token_urlsafe(API_KEY_LENGTH)}"
    
    def create_api_key(self, user_id: int, name: str = None, 
                      scopes: list = None, expires_days: int = None) -> str:
        """Create a new API key for user"""
        key_value = self.generate_api_key()
        
        api_key = APIKey(
            key=key_value,
            user_id=user_id,
            name=name or "Default API Key",
            scopes=scopes or ['read'],
            expires_at=datetime.utcnow() + timedelta(days=expires_days) if expires_days else None
        )
        
        self.db.add(api_key)
        self.db.commit()
        
        return key_value
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[APIUser]:
        """Authenticate user with username/password"""
        user = self.db.query(APIUser).filter(
            APIUser.username == username
        ).first()
        
        if not user or not self.verify_password(password, user.hashed_password):
            return None
            
        if not user.is_active:
            return None
            
        return user
    
    def create_access_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            'sub': str(user_id),
            'exp': expire,
            'iat': datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def get_user_by_api_key(self, api_key: str) -> Optional[APIUser]:
        """Get user by API key"""
        # Check cache first
        if self.cache:
            cache_key = f"api_key_user:{api_key}"
            cached_user_id = self.cache.get(cache_key)
            if cached_user_id:
                user = self.db.query(APIUser).filter(APIUser.id == int(cached_user_id)).first()
                if user and user.is_active:
                    return user
        
        # Check main user table (legacy)
        user = self.db.query(APIUser).filter(
            APIUser.api_key == api_key,
            APIUser.is_active == True
        ).first()
        
        if user:
            # Cache for 5 minutes
            if self.cache:
                self.cache.set(f"api_key_user:{api_key}", str(user.id), ttl=300)
            return user
        
        # Check API keys table
        api_key_obj = self.db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()
        
        if api_key_obj:
            # Check expiration
            if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
                return None
            
            # Update usage
            api_key_obj.last_used_at = datetime.utcnow()
            api_key_obj.usage_count += 1
            self.db.commit()
            
            # Get user
            user = self.db.query(APIUser).filter(
                APIUser.id == api_key_obj.user_id,
                APIUser.is_active == True
            ).first()
            
            if user and self.cache:
                self.cache.set(f"api_key_user:{api_key}", str(user.id), ttl=300)
            
            return user
        
        return None
    
    def check_rate_limit(self, user: APIUser, endpoint: str) -> bool:
        """Check if user has exceeded rate limit"""
        if not self.cache:
            return True  # No rate limiting without cache
        
        # Admin users have no rate limits
        if user.is_admin:
            return True
        
        # Check per-minute limit
        minute_key = f"rate_limit:{user.id}:{endpoint}:minute"
        minute_count = self.cache.get(minute_key) or 0
        
        if int(minute_count) >= user.rate_limit_per_minute:
            logger.warning(f"User {user.username} exceeded minute rate limit")
            return False
        
        # Check per-hour limit
        hour_key = f"rate_limit:{user.id}:{endpoint}:hour"
        hour_count = self.cache.get(hour_key) or 0
        
        if int(hour_count) >= user.rate_limit_per_hour:
            logger.warning(f"User {user.username} exceeded hour rate limit")
            return False
        
        # Increment counters
        self.cache.incr(minute_key)
        self.cache.expire(minute_key, 60)
        
        self.cache.incr(hour_key)
        self.cache.expire(hour_key, 3600)
        
        return True
    
    def track_usage(self, user: APIUser, endpoint: str, response_time: float):
        """Track API usage for billing/analytics"""
        try:
            # Update user stats
            user.total_requests += 1
            user.last_request_at = datetime.utcnow()
            
            # Update monthly usage
            month_key = datetime.utcnow().strftime("%Y-%m")
            if not user.monthly_usage:
                user.monthly_usage = {}
            
            if month_key not in user.monthly_usage:
                user.monthly_usage[month_key] = {
                    'requests': 0,
                    'total_response_time': 0
                }
            
            user.monthly_usage[month_key]['requests'] += 1
            user.monthly_usage[month_key]['total_response_time'] += response_time
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")

# Flask decorators for authentication
def require_api_key(scopes: list = None):
    """Decorator to require API key authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from header or query param
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            # Get database session
            db = get_session()
            cache = getattr(current_app, 'cache_manager', None)
            auth_manager = AuthenticationManager(db, cache)
            
            # Verify API key
            user = auth_manager.get_user_by_api_key(api_key)
            if not user:
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Check rate limit
            endpoint = request.endpoint or 'unknown'
            if not auth_manager.check_rate_limit(user, endpoint):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Check scopes if required
            if scopes:
                # Implementation would check if user has required scopes
                pass
            
            # Add user to request context
            request.api_user = user
            
            # Track timing
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                # Track usage
                response_time = time.time() - start_time
                auth_manager.track_usage(user, endpoint, response_time)
                
                return result
                
            finally:
                db.close()
        
        return decorated_function
    return decorator

def require_jwt_token():
    """Decorator to require JWT token authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Bearer token required'}), 401
            
            token = auth_header.split(' ')[1]
            
            # Get database session
            db = get_session()
            cache = getattr(current_app, 'cache_manager', None)
            auth_manager = AuthenticationManager(db, cache)
            
            # Verify token
            payload = auth_manager.verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Get user
            user_id = int(payload.get('sub'))
            user = db.query(APIUser).filter(APIUser.id == user_id).first()
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Add user to request context
            request.api_user = user
            
            try:
                return f(*args, **kwargs)
            finally:
                db.close()
        
        return decorated_function
    return decorator

def optional_auth():
    """Decorator for optional authentication (enhanced features for authenticated users)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Try to authenticate but don't require it
            api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
            
            if api_key:
                db = get_session()
                cache = getattr(current_app, 'cache_manager', None)
                auth_manager = AuthenticationManager(db, cache)
                
                user = auth_manager.get_user_by_api_key(api_key)
                if user:
                    request.api_user = user
                else:
                    request.api_user = None
                    
                db.close()
            else:
                request.api_user = None
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

import time