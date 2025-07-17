"""
Configuration validation module for production security
Validates all required environment variables and provides secure defaults
"""
import os
import logging
from typing import Dict, List, Optional, Any
from pydantic import Field, validator
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
import secrets

logger = logging.getLogger(__name__)

class SecurityConfig(BaseSettings):
    """Security-related configuration"""
    
    # CORS settings
    allowed_origins: List[str] = Field(default=["http://localhost:3000"], env="ALLOWED_ORIGINS")
    allowed_hosts: List[str] = Field(default=["localhost", "127.0.0.1"], env="ALLOWED_HOSTS")
    
    # API Keys
    ebay_client_id: str = Field(..., env="EBAY_CLIENT_ID")
    ebay_client_secret: str = Field(..., env="EBAY_CLIENT_SECRET") 
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    
    # Application secrets
    secret_key: str = Field(default_factory=lambda: secrets.token_hex(32), env="SECRET_KEY")
    
    # Security flags
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Allow extra fields for development
    class Config:
        env_file = '.env'
        case_sensitive = False
        extra = 'allow'  # Allow extra fields
    
    @validator('allowed_origins', pre=True)
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('allowed_hosts', pre=True) 
    def parse_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    @validator('ebay_client_id')
    def validate_ebay_client_id(cls, v, values):
        # Allow test values in development
        if values.get('environment') == 'development':
            return v  # Allow any value in development
        if not v or v.startswith('your-'):
            raise ValueError("EBAY_CLIENT_ID must be set to your actual eBay API credentials")
        return v
    
    @validator('ebay_client_secret')
    def validate_ebay_client_secret(cls, v, values):
        # Allow test values in development
        if values.get('environment') == 'development':
            return v  # Allow any value in development
        if not v or v.startswith('your-'):
            raise ValueError("EBAY_CLIENT_SECRET must be set to your actual eBay API credentials")
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError("ENVIRONMENT must be one of: development, staging, production")
        return v

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    
    # PostgreSQL settings
    postgres_host: Optional[str] = Field(None, env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_user: Optional[str] = Field(None, env="POSTGRES_USER")
    postgres_password: Optional[str] = Field(None, env="POSTGRES_PASSWORD")
    postgres_db: Optional[str] = Field(None, env="POSTGRES_DB")
    
    # Database URL (takes precedence over individual settings)
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    
    # Connection pool settings
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=300, env="DB_POOL_RECYCLE")
    
    @property
    def get_database_url(self) -> str:
        """Get database URL with proper formatting"""
        if self.database_url:
            # Fix postgres:// to postgresql:// for SQLAlchemy 1.4+
            if self.database_url.startswith("postgres://"):
                return self.database_url.replace("postgres://", "postgresql://", 1)
            return self.database_url
        
        # Build from individual components
        if all([self.postgres_host, self.postgres_user, self.postgres_password, self.postgres_db]):
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        
        # Default to SQLite for development
        return "sqlite:///./findmycar.db"
    
    class Config:
        env_file = '.env'

class RedisConfig(BaseSettings):
    """Redis configuration"""
    
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    class Config:
        env_file = '.env'

class ApplicationConfig(BaseSettings):
    """Main application configuration"""
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    
    @validator('log_level')
    def validate_log_level(cls, v):
        if v.upper() not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        return v.upper()
    
    @validator('log_format')
    def validate_log_format(cls, v):
        if v not in ['json', 'text']:
            raise ValueError("LOG_FORMAT must be either 'json' or 'text'")
        return v
    
    class Config:
        env_file = '.env'

def load_and_validate_config() -> Dict[str, Any]:
    """Load and validate all configuration"""
    try:
        security = SecurityConfig()
        database = DatabaseConfig()
        redis = RedisConfig()
        app = ApplicationConfig()
        
        config = {
            'security': security,
            'database': database,
            'redis': redis,
            'app': app
        }
        
        # Log configuration summary (without secrets)
        logger.info("Configuration loaded successfully:")
        logger.info(f"Environment: {security.environment}")
        logger.info(f"Debug mode: {security.debug}")
        logger.info(f"Database: {database.get_database_url().split('@')[0]}...")
        logger.info(f"Redis: {redis.redis_url.split('@')[0]}...")
        logger.info(f"CORS origins: {security.allowed_origins}")
        logger.info(f"Log level: {app.log_level}")
        
        return config
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

def validate_production_config():
    """Additional validation for production environment"""
    config = load_and_validate_config()
    security = config['security']
    
    if security.environment == 'production':
        issues = []
        
        # Check for insecure defaults
        if security.debug:
            issues.append("DEBUG should be False in production")
        
        if "*" in security.allowed_origins:
            issues.append("CORS should not allow all origins (*) in production")
        
        if security.secret_key == secrets.token_hex(32):
            issues.append("SECRET_KEY should be explicitly set in production")
        
        if "localhost" in security.allowed_hosts and len(security.allowed_hosts) == 1:
            issues.append("ALLOWED_HOSTS should include production domains")
        
        if issues:
            raise ValueError(f"Production configuration issues found:\n" + "\n".join(f"- {issue}" for issue in issues))
    
    return config

if __name__ == "__main__":
    # Test configuration loading
    try:
        config = validate_production_config()
        print("✅ Configuration validation passed!")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        exit(1)