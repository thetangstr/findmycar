#!/usr/bin/env python3
"""
Production Monitoring System
Real-time health monitoring for FindMyCar production deployment
"""
import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionMonitor:
    """Production monitoring and health check system"""
    
    def __init__(self):
        self.production_sources = ['ebay', 'carmax', 'autotrader']
        self.health_history = []
        self.alert_thresholds = {
            'min_vehicles': 30,
            'max_response_time': 45,
            'min_success_rate': 0.8,
            'min_sources_working': 2
        }
    
    def check_source_health(self) -> Dict:
        """Check health of all production sources"""
        print("🔍 Checking Source Health")
        print("-" * 40)
        
        try:
            from unified_source_manager import UnifiedSourceManager
            manager = UnifiedSourceManager()
            
            # Configure for production
            for source_name in manager.source_config.keys():
                if source_name in self.production_sources:
                    manager.enable_source(source_name)
                else:
                    manager.disable_source(source_name)
            
            health_results = {}
            total_vehicles = 0
            working_sources = 0
            
            # Test each source individually
            for source in self.production_sources:
                try:
                    start_time = time.time()
                    result = manager.search_all_sources(
                        query="Honda",
                        year_min=2010,
                        price_max=50000,
                        per_page=5,
                        sources=[source]
                    )
                    response_time = time.time() - start_time
                    
                    vehicles = result.get('total', 0)
                    success = len(result.get('sources_searched', [])) > 0 and vehicles > 0
                    
                    health_results[source] = {
                        'status': 'healthy' if success else 'unhealthy',
                        'vehicles': vehicles,
                        'response_time': response_time,
                        'success': success,
                        'last_check': datetime.now().isoformat()
                    }
                    
                    if success:
                        total_vehicles += vehicles
                        working_sources += 1
                        print(f"  ✅ {source}: {vehicles} vehicles ({response_time:.2f}s)")
                    else:
                        print(f"  ❌ {source}: failed or no vehicles")
                
                except Exception as e:
                    health_results[source] = {
                        'status': 'error',
                        'vehicles': 0,
                        'response_time': 0,
                        'success': False,
                        'error': str(e),
                        'last_check': datetime.now().isoformat()
                    }
                    print(f"  💥 {source}: error - {str(e)}")
            
            # Overall health assessment
            overall_health = {
                'timestamp': datetime.now().isoformat(),
                'sources': health_results,
                'summary': {
                    'total_vehicles': total_vehicles,
                    'working_sources': working_sources,
                    'total_sources': len(self.production_sources),
                    'success_rate': working_sources / len(self.production_sources),
                    'overall_status': 'healthy' if working_sources >= 2 and total_vehicles >= 30 else 'degraded'
                }
            }
            
            print(f"\nOverall: {working_sources}/{len(self.production_sources)} sources, {total_vehicles} vehicles")
            return overall_health
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'summary': {
                    'overall_status': 'error'
                }
            }
    
    def test_unified_search(self) -> Dict:
        """Test unified search performance"""
        print("\n🔄 Testing Unified Search Performance")
        print("-" * 40)
        
        try:
            from unified_source_manager import UnifiedSourceManager
            manager = UnifiedSourceManager()
            
            # Configure for production
            for source_name in manager.source_config.keys():
                if source_name in self.production_sources:
                    manager.enable_source(source_name)
                else:
                    manager.disable_source(source_name)
            
            # Test search
            start_time = time.time()
            result = manager.search_all_sources(
                query="Honda",
                year_min=2010,
                price_max=50000,
                per_page=15
            )
            search_time = time.time() - start_time
            
            total_vehicles = result.get('total', 0)
            sources_succeeded = result.get('sources_searched', [])
            sources_failed = result.get('sources_failed', [])
            
            # Vehicle distribution
            source_distribution = {}
            for vehicle in result.get('vehicles', []):
                source = vehicle.get('source', 'unknown')
                source_distribution[source] = source_distribution.get(source, 0) + 1
            
            search_health = {
                'timestamp': datetime.now().isoformat(),
                'total_vehicles': total_vehicles,
                'search_time': search_time,
                'sources_succeeded': len(sources_succeeded),
                'sources_failed': len(sources_failed),
                'distribution': source_distribution,
                'performance_score': self._calculate_performance_score(total_vehicles, search_time, len(sources_succeeded)),
                'status': 'healthy' if total_vehicles >= 30 and search_time < 45 and len(sources_succeeded) >= 2 else 'degraded'
            }
            
            print(f"  Vehicles: {total_vehicles}, Time: {search_time:.2f}s")
            print(f"  Sources: {len(sources_succeeded)} succeeded, {len(sources_failed)} failed")
            print(f"  Distribution: {source_distribution}")
            
            return search_health
            
        except Exception as e:
            logger.error(f"Search test failed: {str(e)}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
    
    def _calculate_performance_score(self, vehicles: int, time: float, sources: int) -> float:
        """Calculate performance score (0-100)"""
        vehicle_score = min(vehicles / 50 * 40, 40)  # 40 points max for vehicles
        time_score = max(0, (60 - time) / 60 * 30)   # 30 points max for speed
        source_score = sources / 3 * 30              # 30 points max for sources
        return round(vehicle_score + time_score + source_score, 1)
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        print("\n📊 Generating Health Report")
        print("=" * 60)
        
        # Get source health
        source_health = self.check_source_health()
        
        # Get search performance
        search_health = self.test_unified_search()
        
        # Environment check
        env_health = {
            'ebay_configured': bool(os.getenv('EBAY_CLIENT_ID') and os.getenv('EBAY_CLIENT_SECRET')),
            'database_configured': bool(os.getenv('DATABASE_URL')),
            'secret_key_configured': bool(os.getenv('SECRET_KEY')),
            'redis_available': bool(os.getenv('REDIS_URL'))
        }
        
        # Overall assessment
        overall_status = 'healthy'
        alerts = []
        
        # Check thresholds
        if search_health.get('total_vehicles', 0) < self.alert_thresholds['min_vehicles']:
            overall_status = 'degraded'
            alerts.append(f"Low vehicle count: {search_health.get('total_vehicles', 0)} < {self.alert_thresholds['min_vehicles']}")
        
        if search_health.get('search_time', 999) > self.alert_thresholds['max_response_time']:
            overall_status = 'degraded'
            alerts.append(f"Slow response: {search_health.get('search_time', 0):.1f}s > {self.alert_thresholds['max_response_time']}s")
        
        working_sources = source_health.get('summary', {}).get('working_sources', 0)
        if working_sources < self.alert_thresholds['min_sources_working']:
            overall_status = 'critical'
            alerts.append(f"Too few working sources: {working_sources} < {self.alert_thresholds['min_sources_working']}")
        
        # Compile report
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'alerts': alerts,
            'environment': env_health,
            'sources': source_health,
            'search_performance': search_health,
            'performance_score': search_health.get('performance_score', 0),
            'uptime_info': {
                'check_duration': 'single_check',
                'next_check': (datetime.now() + timedelta(minutes=5)).isoformat()
            }
        }
        
        # Add to history
        self.health_history.append(report)
        
        # Keep only last 24 hours of history
        cutoff = datetime.now() - timedelta(hours=24)
        self.health_history = [
            r for r in self.health_history 
            if datetime.fromisoformat(r['timestamp']) > cutoff
        ]
        
        return report
    
    def print_health_summary(self, report: Dict):
        """Print human-readable health summary"""
        status = report.get('overall_status', 'unknown')
        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️',
            'critical': '❌',
            'error': '💥'
        }.get(status, '❓')
        
        print(f"\n{status_emoji} SYSTEM STATUS: {status.upper()}")
        print("=" * 60)
        
        # Performance score
        score = report.get('performance_score', 0)
        print(f"Performance Score: {score}/100")
        
        # Key metrics
        search = report.get('search_performance', {})
        print(f"Vehicles Available: {search.get('total_vehicles', 0)}")
        print(f"Response Time: {search.get('search_time', 0):.2f}s")
        print(f"Sources Working: {search.get('sources_succeeded', 0)}/3")
        
        # Alerts
        alerts = report.get('alerts', [])
        if alerts:
            print(f"\n⚠️ ALERTS ({len(alerts)}):")
            for alert in alerts:
                print(f"  • {alert}")
        else:
            print(f"\n✅ No alerts - system operating normally")
        
        # Environment
        env = report.get('environment', {})
        env_ok = sum(env.values())
        print(f"\nEnvironment: {env_ok}/{len(env)} components configured")
        
        # Next steps
        if status == 'healthy':
            print("\n💡 System is operating optimally")
        elif status == 'degraded':
            print("\n💡 System is functional but performance is degraded")
            print("   Consider investigating slow sources or network issues")
        elif status == 'critical':
            print("\n💡 System requires immediate attention")
            print("   Multiple sources failing - check API credentials and network")
        
        print("=" * 60)
    
    def save_report(self, report: Dict, filename: str = None):
        """Save health report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filename}")

def main():
    """Run production monitoring"""
    print("🔍 FindMyCar Production Monitor")
    print("=" * 80)
    
    monitor = ProductionMonitor()
    
    try:
        # Generate health report
        report = monitor.generate_health_report()
        
        # Print summary
        monitor.print_health_summary(report)
        
        # Save report
        monitor.save_report(report)
        
        # Return exit code based on status
        status = report.get('overall_status', 'error')
        return 0 if status in ['healthy', 'degraded'] else 1
        
    except Exception as e:
        print(f"💥 Monitoring failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)