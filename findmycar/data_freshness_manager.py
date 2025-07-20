#!/usr/bin/env python3
"""
Data freshness management and update strategies for production
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from sqlalchemy import text
from sqlalchemy.orm import Session
import json
import hashlib
from enum import Enum

logger = logging.getLogger(__name__)

class FreshnessLevel(Enum):
    """Data freshness levels"""
    REAL_TIME = "real_time"      # < 5 minutes
    FRESH = "fresh"               # < 1 hour  
    RECENT = "recent"             # < 24 hours
    STALE = "stale"               # < 7 days
    EXPIRED = "expired"           # > 7 days

class UpdateStrategy(Enum):
    """Update strategies for data refresh"""
    LAZY = "lazy"                 # Update on demand
    EAGER = "eager"               # Update proactively
    SCHEDULED = "scheduled"       # Update on schedule
    HYBRID = "hybrid"             # Combination of strategies

class DataFreshnessManager:
    """Manages data freshness and update strategies"""
    
    # Freshness thresholds in seconds
    FRESHNESS_THRESHOLDS = {
        FreshnessLevel.REAL_TIME: 300,      # 5 minutes
        FreshnessLevel.FRESH: 3600,         # 1 hour
        FreshnessLevel.RECENT: 86400,       # 24 hours
        FreshnessLevel.STALE: 604800,       # 7 days
    }
    
    # Update priorities by data type
    UPDATE_PRIORITIES = {
        'price': 1,          # Highest priority - prices change frequently
        'availability': 2,   # High priority - vehicles sell quickly
        'mileage': 3,       # Medium priority - changes occasionally
        'description': 4,    # Low priority - rarely changes
        'features': 5        # Lowest priority - static data
    }
    
    def __init__(self, db: Session, cache_manager=None):
        self.db = db
        self.cache = cache_manager
        self.update_queue = []
        self.last_update_times = {}
        
    def get_data_freshness(self, last_updated: datetime) -> FreshnessLevel:
        """Determine freshness level of data based on last update time"""
        if not last_updated:
            return FreshnessLevel.EXPIRED
            
        age = (datetime.utcnow() - last_updated).total_seconds()
        
        if age < self.FRESHNESS_THRESHOLDS[FreshnessLevel.REAL_TIME]:
            return FreshnessLevel.REAL_TIME
        elif age < self.FRESHNESS_THRESHOLDS[FreshnessLevel.FRESH]:
            return FreshnessLevel.FRESH
        elif age < self.FRESHNESS_THRESHOLDS[FreshnessLevel.RECENT]:
            return FreshnessLevel.RECENT
        elif age < self.FRESHNESS_THRESHOLDS[FreshnessLevel.STALE]:
            return FreshnessLevel.STALE
        else:
            return FreshnessLevel.EXPIRED
    
    def should_refresh_data(self, 
                          data_type: str,
                          last_updated: datetime,
                          strategy: UpdateStrategy = UpdateStrategy.HYBRID) -> bool:
        """Determine if data should be refreshed based on strategy"""
        
        freshness = self.get_data_freshness(last_updated)
        
        if strategy == UpdateStrategy.EAGER:
            # Refresh if not real-time fresh
            return freshness != FreshnessLevel.REAL_TIME
            
        elif strategy == UpdateStrategy.LAZY:
            # Only refresh if expired
            return freshness == FreshnessLevel.EXPIRED
            
        elif strategy == UpdateStrategy.SCHEDULED:
            # Check if scheduled update is due
            return self._is_scheduled_update_due(data_type, last_updated)
            
        else:  # HYBRID
            # Use intelligent strategy based on data type and usage
            return self._hybrid_refresh_decision(data_type, freshness, last_updated)
    
    def _hybrid_refresh_decision(self, 
                               data_type: str,
                               freshness: FreshnessLevel,
                               last_updated: datetime) -> bool:
        """Make intelligent refresh decision based on multiple factors"""
        
        # Always refresh expired data
        if freshness == FreshnessLevel.EXPIRED:
            return True
        
        # High priority data types refresh more frequently
        priority = self.UPDATE_PRIORITIES.get(data_type, 5)
        
        if priority <= 2:  # High priority (price, availability)
            return freshness not in [FreshnessLevel.REAL_TIME, FreshnessLevel.FRESH]
        elif priority <= 3:  # Medium priority
            return freshness in [FreshnessLevel.STALE, FreshnessLevel.EXPIRED]
        else:  # Low priority
            return freshness == FreshnessLevel.EXPIRED
    
    def _is_scheduled_update_due(self, data_type: str, last_updated: datetime) -> bool:
        """Check if scheduled update is due"""
        # Define update schedules
        schedules = {
            'price': timedelta(hours=6),
            'availability': timedelta(hours=12),
            'mileage': timedelta(days=1),
            'description': timedelta(days=7),
            'features': timedelta(days=30)
        }
        
        schedule = schedules.get(data_type, timedelta(days=7))
        return datetime.utcnow() - last_updated > schedule
    
    def track_data_access(self, data_id: str, data_type: str):
        """Track when data is accessed to inform refresh decisions"""
        access_key = f"access:{data_type}:{data_id}"
        
        # Track in cache
        if self.cache:
            # Increment access counter
            current = self.cache.get(access_key) or 0
            self.cache.set(access_key, current + 1, ttl=86400)  # 24 hour TTL
            
            # Track last access time
            self.cache.set(f"{access_key}:last", datetime.utcnow().isoformat(), ttl=86400)
    
    def get_stale_vehicles(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get vehicles that need updating"""
        query = text("""
            SELECT 
                id,
                listing_id,
                source,
                make,
                model,
                year,
                last_seen_at,
                updated_at,
                EXTRACT(EPOCH FROM (NOW() - last_seen_at)) as age_seconds
            FROM vehicles_v2
            WHERE is_active = true
                AND (
                    last_seen_at < NOW() - INTERVAL '24 hours'
                    OR last_seen_at IS NULL
                )
            ORDER BY 
                last_seen_at ASC NULLS FIRST,
                updated_at ASC
            LIMIT :limit
        """)
        
        try:
            result = self.db.execute(query, {'limit': limit})
            vehicles = []
            
            for row in result:
                vehicles.append({
                    'id': row.id,
                    'listing_id': row.listing_id,
                    'source': row.source,
                    'make': row.make,
                    'model': row.model,
                    'year': row.year,
                    'last_seen_at': row.last_seen_at,
                    'updated_at': row.updated_at,
                    'age_seconds': row.age_seconds,
                    'freshness': self.get_data_freshness(row.last_seen_at).value
                })
            
            return vehicles
            
        except Exception as e:
            logger.error(f"Error getting stale vehicles: {e}")
            return []
    
    def mark_vehicle_updated(self, vehicle_id: int, success: bool = True):
        """Mark vehicle as updated"""
        try:
            if success:
                query = text("""
                    UPDATE vehicles_v2 
                    SET last_seen_at = NOW(),
                        updated_at = NOW()
                    WHERE id = :id
                """)
            else:
                # Just update the attempt time
                query = text("""
                    UPDATE vehicles_v2 
                    SET last_update_attempt = NOW()
                    WHERE id = :id
                """)
            
            self.db.execute(query, {'id': vehicle_id})
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error marking vehicle updated: {e}")
            self.db.rollback()
    
    def get_update_statistics(self) -> Dict[str, Any]:
        """Get statistics about data freshness"""
        try:
            stats_query = text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN last_seen_at > NOW() - INTERVAL '5 minutes' THEN 1 END) as real_time,
                    COUNT(CASE WHEN last_seen_at > NOW() - INTERVAL '1 hour' THEN 1 END) as fresh,
                    COUNT(CASE WHEN last_seen_at > NOW() - INTERVAL '24 hours' THEN 1 END) as recent,
                    COUNT(CASE WHEN last_seen_at > NOW() - INTERVAL '7 days' THEN 1 END) as stale,
                    COUNT(CASE WHEN last_seen_at <= NOW() - INTERVAL '7 days' 
                          OR last_seen_at IS NULL THEN 1 END) as expired
                FROM vehicles_v2
                WHERE is_active = true
            """)
            
            result = self.db.execute(stats_query).fetchone()
            
            return {
                'total_active_vehicles': result.total,
                'freshness_distribution': {
                    'real_time': result.real_time,
                    'fresh': result.fresh - result.real_time,
                    'recent': result.recent - result.fresh,
                    'stale': result.stale - result.recent,
                    'expired': result.expired
                },
                'freshness_percentages': {
                    'real_time': round(result.real_time / result.total * 100, 1) if result.total > 0 else 0,
                    'fresh': round((result.fresh - result.real_time) / result.total * 100, 1) if result.total > 0 else 0,
                    'recent': round((result.recent - result.fresh) / result.total * 100, 1) if result.total > 0 else 0,
                    'stale': round((result.stale - result.recent) / result.total * 100, 1) if result.total > 0 else 0,
                    'expired': round(result.expired / result.total * 100, 1) if result.total > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting update statistics: {e}")
            return {}
    
    def prioritize_updates(self, vehicles: List[Dict]) -> List[Dict]:
        """Prioritize vehicles for updating based on various factors"""
        
        def calculate_priority_score(vehicle: Dict) -> float:
            score = 0.0
            
            # Age factor (older = higher priority)
            age_seconds = vehicle.get('age_seconds', 0)
            age_days = age_seconds / 86400
            score += min(age_days * 10, 100)  # Max 100 points for age
            
            # Source factor (some sources change more frequently)
            source_weights = {
                'ebay': 1.5,      # eBay listings change frequently
                'carmax': 1.2,    # CarMax updates regularly
                'autotrader': 1.0,
                'local': 0.5      # Local data doesn't need frequent updates
            }
            score *= source_weights.get(vehicle.get('source', ''), 1.0)
            
            # Popular vehicle factor (frequently accessed)
            if self.cache:
                access_key = f"access:vehicle:{vehicle.get('id')}"
                access_count = self.cache.get(access_key) or 0
                score += min(access_count * 5, 50)  # Max 50 points for popularity
            
            # Price range factor (higher priced = more important to keep fresh)
            # This would require price data, skipping for now
            
            return score
        
        # Sort by priority score (highest first)
        vehicles_with_scores = [
            {**v, 'priority_score': calculate_priority_score(v)}
            for v in vehicles
        ]
        
        return sorted(vehicles_with_scores, key=lambda x: x['priority_score'], reverse=True)
    
    def create_update_batch(self, 
                           batch_size: int = 50,
                           strategy: UpdateStrategy = UpdateStrategy.HYBRID) -> List[Dict]:
        """Create a batch of vehicles to update"""
        
        # Get stale vehicles
        stale_vehicles = self.get_stale_vehicles(limit=batch_size * 2)
        
        if not stale_vehicles:
            logger.info("No stale vehicles found for updating")
            return []
        
        # Prioritize updates
        prioritized = self.prioritize_updates(stale_vehicles)
        
        # Select batch based on strategy
        if strategy == UpdateStrategy.EAGER:
            # Take all up to batch size
            batch = prioritized[:batch_size]
        elif strategy == UpdateStrategy.LAZY:
            # Only take expired ones
            batch = [v for v in prioritized if v['freshness'] == 'expired'][:batch_size]
        else:
            # Take top priority ones
            batch = prioritized[:batch_size]
        
        logger.info(f"Created update batch of {len(batch)} vehicles")
        return batch
    
    def estimate_update_time(self, batch_size: int) -> Dict[str, float]:
        """Estimate time required to update a batch of vehicles"""
        
        # Average update times per source (seconds)
        source_times = {
            'ebay': 0.5,        # API call
            'carmax': 5.0,      # Web scraping
            'autotrader': 5.0,  # Web scraping
            'local': 0.1        # Database update
        }
        
        # Get distribution of sources in batch
        batch = self.create_update_batch(batch_size, strategy=UpdateStrategy.LAZY)
        source_counts = {}
        
        for vehicle in batch:
            source = vehicle.get('source', 'local')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Calculate estimates
        total_time = 0
        time_by_source = {}
        
        for source, count in source_counts.items():
            time_estimate = count * source_times.get(source, 1.0)
            time_by_source[source] = time_estimate
            total_time += time_estimate
        
        return {
            'total_seconds': total_time,
            'total_minutes': total_time / 60,
            'by_source': time_by_source,
            'vehicles_count': len(batch)
        }