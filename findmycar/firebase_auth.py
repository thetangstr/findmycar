"""
Firebase Authentication Module
Handles Google OAuth and user management
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import httpx
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from sqlalchemy.orm import Session
from database import User, get_db

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
    firebase_initialized = True
except Exception as e:
    logger.warning(f"Firebase Admin SDK initialization failed: {e}")
    firebase_initialized = False

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# HTTP Bearer for JWT tokens
security = HTTPBearer()


class FirebaseAuth:
    """Firebase authentication handler"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def verify_google_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify Google ID token and return user info
        """
        if not firebase_initialized:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
            
        try:
            # Verify the ID token
            decoded_token = firebase_auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            
            # Get or create user
            user = await self.get_or_create_user(decoded_token)
            
            # Create session
            session_token = self.create_session_token(user)
            
            return {
                "user": {
                    "uid": user.uid,
                    "email": user.email,
                    "display_name": user.display_name,
                    "photo_url": user.photo_url,
                    "created_at": user.created_at.isoformat()
                },
                "access_token": session_token,
                "token_type": "bearer"
            }
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    async def get_or_create_user(self, token_data: Dict[str, Any]) -> User:
        """
        Get existing user or create new one
        """
        uid = token_data['uid']
        email = token_data.get('email', '')
        display_name = token_data.get('name', '')
        photo_url = token_data.get('picture', '')
        
        # Check if user exists
        user = self.db.query(User).filter(User.uid == uid).first()
        
        if user:
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user
        else:
            # Create new user
            user = User(
                uid=uid,
                email=email,
                display_name=display_name,
                photo_url=photo_url
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
    
    def create_session_token(self, user: User) -> str:
        """
        Create JWT session token
        """
        payload = {
            "uid": user.uid,
            "email": user.email,
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    async def verify_session_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT session token
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            
            # Get user from database
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            return {
                "id": user.id,
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "photo_url": user.photo_url
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def logout(self, token: str):
        """
        Logout user (invalidate token)
        """
        # In a production system, you might want to maintain a blacklist
        # For now, we'll just rely on token expiration
        pass
    
    async def delete_user(self, uid: str):
        """
        Delete user account
        """
        try:
            # Delete from Firebase Auth if available
            if firebase_initialized:
                firebase_auth.delete_user(uid)
            
            # Delete from database
            user = self.db.query(User).filter(User.uid == uid).first()
            if user:
                self.db.delete(user)
                self.db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False


# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get current authenticated user
    """
    auth_handler = FirebaseAuth(db)
    token = credentials.credentials
    return await auth_handler.verify_session_token(token)


# Optional dependency - returns None if not authenticated
async def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise None
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        auth_handler = FirebaseAuth(db)
        return await auth_handler.verify_session_token(token)
    except:
        return None