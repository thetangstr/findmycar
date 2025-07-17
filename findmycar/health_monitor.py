"""
Health Monitor for CarGPT Data Sources
Real-time monitoring and alerting for all integrated data sources
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import requests
from test_framework import DataSourceTestFramework, TestStatus

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthMetric:
    source: str
    status: HealthStatus
    response_time: float
    success_rate: float
    last_successful: datetime
    last_checked: datetime
    error_message: Optional[str] = None
    data_points: int = 0

class DataSourceHealthMonitor:
    """
    Continuous health monitoring for all CarGPT data sources
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.test_framework = DataSourceTestFramework()
        self.health_metrics: Dict[str, HealthMetric] = {}
        
        # Health check configuration
        self.sources = ['ebay', 'carmax', 'bringatrailer', 'cars_com', 'autodev']
        self.check_interval = 300  # 5 minutes
        self.quick_check_queries = ["Honda Civic", "Toyota Camry"]
        
        # Thresholds
        self.response_time_threshold = 30.0  # seconds
        self.success_rate_threshold = 0.8    # 80%
        self.degraded_threshold = 0.6        # 60%
        
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("Starting CarGPT data source health monitoring")
        
        while True:
            try:
                await self._run_health_checks()
                await self._update_health_cache()
                await self._check_alerts()
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _run_health_checks(self):
        """Run health checks for all data sources"""
        logger.info("Running health checks for all data sources")
        
        # Run checks concurrently
        tasks = []
        for source in self.sources:
            task = asyncio.create_task(self._check_source_health(source))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_source_health(self, source: str):
        """Check health of a specific data source"""
        start_time = time.time()
        
        try:
            # Perform quick connectivity and search test
            if source == 'ebay':
                success, data_points, error = await self._quick_test_ebay()
            elif source == 'carmax':
                success, data_points, error = await self._quick_test_carmax()
            elif source == 'bringatrailer':
                success, data_points, error = await self._quick_test_bat()
            elif source == 'cars_com':
                success, data_points, error = await self._quick_test_cars()
            elif source == 'autodev':
                success, data_points, error = await self._quick_test_autodev()
            else:
                success, data_points, error = False, 0, "Unknown source"
            
            response_time = time.time() - start_time
            
            # Update success rate (rolling average)
            current_metric = self.health_metrics.get(source)
            if current_metric:
                # Simple moving average of last 10 checks
                old_rate = current_metric.success_rate
                new_rate = (old_rate * 9 + (1.0 if success else 0.0)) / 10
                success_rate = new_rate
                last_successful = datetime.now() if success else current_metric.last_successful
            else:
                success_rate = 1.0 if success else 0.0
                last_successful = datetime.now() if success else datetime.min
            
            # Determine health status
            if success and response_time <= self.response_time_threshold:
                status = HealthStatus.HEALTHY
            elif success_rate >= self.degraded_threshold:
                status = HealthStatus.DEGRADED
            elif success_rate >= 0.2:  # 20% minimum
                status = HealthStatus.UNHEALTHY
            else:
                status = HealthStatus.UNKNOWN
            
            # Update health metric
            self.health_metrics[source] = HealthMetric(
                source=source,
                status=status,
                response_time=response_time,
                success_rate=success_rate,
                last_successful=last_successful,
                last_checked=datetime.now(),
                error_message=error,
                data_points=data_points
            )
            
            logger.info(f"{source}: {status.value} ({response_time:.2f}s, {success_rate:.1%} success)")
            
        except Exception as e:
            logger.error(f"Health check failed for {source}: {e}")
            
            # Mark as unhealthy
            self.health_metrics[source] = HealthMetric(
                source=source,
                status=HealthStatus.UNHEALTHY,
                response_time=999.0,
                success_rate=0.0,
                last_successful=datetime.min,
                last_checked=datetime.now(),
                error_message=str(e),
                data_points=0
            )
    
    # Quick test methods for each data source
    
    async def _quick_test_ebay(self) -> tuple[bool, int, Optional[str]]:
        """Quick test of eBay Motors"""
        try:
            results = self.test_framework._search_ebay("Honda Civic", limit=3)
            return len(results) > 0, len(results), None
        except Exception as e:
            return False, 0, str(e)
    
    async def _quick_test_carmax(self) -> tuple[bool, int, Optional[str]]:
        """Quick test of CarMax"""
        try:
            results = self.test_framework._search_carmax("Toyota Camry", limit=3)
            return len(results) > 0, len(results), None
        except Exception as e:
            return False, 0, str(e)
    
    async def _quick_test_bat(self) -> tuple[bool, int, Optional[str]]:
        """Quick test of Bring a Trailer"""
        try:
            results = self.test_framework._search_bat("BMW", limit=3)
            return len(results) >= 0, len(results), None  # BaT might have 0 results and still be healthy
        except Exception as e:
            return False, 0, str(e)
    
    async def _quick_test_cars(self) -> tuple[bool, int, Optional[str]]:
        """Quick test of Cars.com"""
        try:
            results = self.test_framework._search_cars("Honda Civic", limit=3)
            return len(results) > 0, len(results), None
        except Exception as e:
            return False, 0, str(e)
    
    async def _quick_test_autodev(self) -> tuple[bool, int, Optional[str]]:
        """Quick test of Auto.dev"""
        try:
            results = self.test_framework._search_autodev("Toyota Camry", limit=3)
            return len(results) > 0, len(results), None
        except Exception as e:
            return False, 0, str(e)
    
    async def _update_health_cache(self):
        """Update health status in Redis cache"""
        if not self.redis_client:
            return
        
        try:
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': self._calculate_overall_health(),
                'sources': {
                    source: asdict(metric) 
                    for source, metric in self.health_metrics.items()
                }
            }
            
            # Convert datetime objects to strings for JSON serialization
            for source_data in health_data['sources'].values():
                source_data['last_successful'] = source_data['last_successful'].isoformat()
                source_data['last_checked'] = source_data['last_checked'].isoformat()
                source_data['status'] = source_data['status'].value
            
            self.redis_client.setex(
                'cargpt:health:status',
                3600,  # 1 hour expiry
                json.dumps(health_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to update health cache: {e}")
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall system health"""
        if not self.health_metrics:
            return HealthStatus.UNKNOWN.value
        
        healthy_count = sum(1 for m in self.health_metrics.values() if m.status == HealthStatus.HEALTHY)
        degraded_count = sum(1 for m in self.health_metrics.values() if m.status == HealthStatus.DEGRADED)
        total_count = len(self.health_metrics)
        
        healthy_percentage = healthy_count / total_count
        
        if healthy_percentage >= 0.8:  # 80% healthy
            return HealthStatus.HEALTHY.value
        elif (healthy_count + degraded_count) / total_count >= 0.6:  # 60% functional
            return HealthStatus.DEGRADED.value
        else:
            return HealthStatus.UNHEALTHY.value
    
    async def _check_alerts(self):
        """Check if any alerts should be triggered"""
        for source, metric in self.health_metrics.items():
            
            # Alert on unhealthy status
            if metric.status == HealthStatus.UNHEALTHY:
                await self._send_alert(
                    f"UNHEALTHY: {source}",
                    f"Data source {source} is unhealthy. "
                    f"Success rate: {metric.success_rate:.1%}, "
                    f"Last error: {metric.error_message}"
                )
            
            # Alert on prolonged degradation
            elif metric.status == HealthStatus.DEGRADED:
                time_since_healthy = datetime.now() - metric.last_successful
                if time_since_healthy > timedelta(hours=1):
                    await self._send_alert(
                        f"DEGRADED: {source}",
                        f"Data source {source} has been degraded for {time_since_healthy}. "
                        f"Success rate: {metric.success_rate:.1%}"
                    )
            
            # Alert on slow response times
            if metric.response_time > self.response_time_threshold * 2:
                await self._send_alert(
                    f"SLOW: {source}",
                    f"Data source {source} is responding slowly: {metric.response_time:.2f}s"
                )
    
    async def _send_alert(self, title: str, message: str):
        """Send alert notification"""
        logger.warning(f"ALERT - {title}: {message}")
        
        # Here you could integrate with:
        # - Slack webhook
        # - Email service
        # - PagerDuty
        # - Discord webhook
        # etc.
        
        # Example Slack webhook (uncomment and configure)
        # await self._send_slack_alert(title, message)
    
    async def _send_slack_alert(self, title: str, message: str):
        """Send alert to Slack (example implementation)"""
        # webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        # if not webhook_url:
        #     return
        # 
        # payload = {
        #     "text": f"🚨 CarGPT Alert: {title}",
        #     "attachments": [{
        #         "color": "danger",
        #         "fields": [{
        #             "title": "Details",
        #             "value": message,
        #             "short": False
        #         }]
        #     }]
        # }
        # 
        # try:
        #     async with aiohttp.ClientSession() as session:
        #         async with session.post(webhook_url, json=payload) as response:
        #             if response.status != 200:
        #                 logger.error(f"Failed to send Slack alert: {response.status}")
        # except Exception as e:
        #     logger.error(f"Error sending Slack alert: {e}")
        pass
    
    def get_health_status(self) -> Dict:
        """Get current health status for API endpoint"""
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': self._calculate_overall_health(),
            'sources': {
                source: {
                    'status': metric.status.value,
                    'response_time': metric.response_time,
                    'success_rate': metric.success_rate,
                    'last_successful': metric.last_successful.isoformat(),
                    'last_checked': metric.last_checked.isoformat(),
                    'error_message': metric.error_message,
                    'data_points': metric.data_points
                }
                for source, metric in self.health_metrics.items()
            }
        }
    
    async def run_comprehensive_test(self) -> Dict:
        """Run comprehensive test suite on demand"""
        logger.info("Running comprehensive data source tests")
        
        results = self.test_framework.run_all_tests()
        
        # Update health metrics based on comprehensive results
        for source, test_results in results.items():
            passed_tests = sum(1 for r in test_results if r.status == TestStatus.PASS)
            total_tests = len(test_results)
            success_rate = passed_tests / total_tests if total_tests > 0 else 0.0
            
            avg_response_time = sum(r.execution_time for r in test_results) / total_tests if total_tests > 0 else 0.0
            
            # Determine status
            if success_rate >= self.success_rate_threshold:
                status = HealthStatus.HEALTHY
            elif success_rate >= self.degraded_threshold:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            self.health_metrics[source] = HealthMetric(
                source=source,
                status=status,
                response_time=avg_response_time,
                success_rate=success_rate,
                last_successful=datetime.now() if success_rate > 0 else datetime.min,
                last_checked=datetime.now(),
                error_message=None,
                data_points=sum(r.data_points for r in test_results)
            )
        
        return self.get_health_status()

# Standalone health check function for API endpoints
def get_current_health_status(redis_client=None) -> Dict:
    """Get current health status from cache or run quick check"""
    if redis_client:
        try:
            cached_data = redis_client.get('cargpt:health:status')
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Failed to get cached health status: {e}")
    
    # Fallback to quick status check
    monitor = DataSourceHealthMonitor(redis_client)
    return {
        'timestamp': datetime.now().isoformat(),
        'overall_status': 'unknown',
        'sources': {source: {'status': 'unknown'} for source in monitor.sources},
        'note': 'Health monitoring not active'
    }

# CLI interface for manual testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CarGPT Health Monitor")
    parser.add_argument("--mode", choices=["monitor", "test", "status"], default="status",
                       help="Mode: continuous monitoring, one-time test, or status check")
    parser.add_argument("--interval", type=int, default=300,
                       help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    monitor = DataSourceHealthMonitor()
    
    if args.mode == "monitor":
        monitor.check_interval = args.interval
        asyncio.run(monitor.start_monitoring())
    elif args.mode == "test":
        result = asyncio.run(monitor.run_comprehensive_test())
        print(json.dumps(result, indent=2))
    else:
        status = monitor.get_health_status()
        print(json.dumps(status, indent=2))