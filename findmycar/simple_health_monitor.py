#!/usr/bin/env python3
"""
Simple health monitor for production app
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Simple health monitor for production application"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
    
    def get_detailed_status(self, db: Session) -> Dict[str, Any]:
        """Get detailed health status of all components"""
        components = []
        
        # Database health
        try:
            from sqlalchemy import text
            result = db.execute(text("SELECT 1")).scalar()
            db_status = 'healthy' if result == 1 else 'unhealthy'
            db_message = 'Database connection OK'
        except Exception as e:
            db_status = 'unhealthy'
            db_message = f'Database error: {str(e)}'
        
        components.append({
            'name': 'database',
            'status': db_status,
            'message': db_message,
            'checked_at': datetime.utcnow().isoformat()
        })
        
        # eBay API health
        try:
            # Check if we have API credentials
            if os.environ.get('EBAY_CLIENT_ID') and os.environ.get('EBAY_CLIENT_SECRET'):
                ebay_status = 'healthy'
                ebay_message = 'eBay API credentials configured'
            else:
                ebay_status = 'degraded'
                ebay_message = 'eBay API credentials missing'
        except Exception as e:
            ebay_status = 'unhealthy'
            ebay_message = f'eBay check error: {str(e)}'
        
        components.append({
            'name': 'ebay_api',
            'status': ebay_status,
            'message': ebay_message,
            'checked_at': datetime.utcnow().isoformat()
        })
        
        # Cache health
        try:
            from cache_manager import cache_manager
            cache_stats = cache_manager.cache_stats()
            cache_status = 'healthy' if cache_stats['enabled'] else 'degraded'
            cache_message = f"Cache type: {cache_stats['type']}, Hit rate: {cache_stats['hit_rate']:.2%}"
        except Exception as e:
            cache_status = 'unhealthy'
            cache_message = f'Cache error: {str(e)}'
        
        components.append({
            'name': 'cache',
            'status': cache_status,
            'message': cache_message,
            'checked_at': datetime.utcnow().isoformat()
        })
        
        # Calculate overall status
        statuses = [c['status'] for c in components]
        if all(s == 'healthy' for s in statuses):
            overall_status = 'healthy'
        elif any(s == 'unhealthy' for s in statuses):
            overall_status = 'unhealthy'
        else:
            overall_status = 'degraded'
        
        # Calculate uptime
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': uptime_seconds,
            'uptime_human': self._format_uptime(uptime_seconds),
            'components': components,
            'version': os.environ.get('APP_VERSION', '1.0.0'),
            'environment': os.environ.get('ENVIRONMENT', 'production')
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        
        return " ".join(parts) if parts else "< 1m"