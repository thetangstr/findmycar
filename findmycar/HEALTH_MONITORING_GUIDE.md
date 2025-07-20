# Comprehensive Health Monitoring Guide

## Overview

The FindMyCar production Flask application now includes comprehensive health monitoring capabilities that provide detailed insights into system performance, component health, and operational metrics.

## Health Monitoring Endpoints

### 1. Basic Health Check - `/health`
- **Purpose**: Quick health check for load balancers and basic monitoring
- **Method**: GET
- **Response**: JSON with basic status information
```json
{
  "status": "healthy",
  "service": "findmycar-production",
  "timestamp": "2024-01-18T10:30:00",
  "version": "1.0.0"
}
```

### 2. Detailed Health Check - `/health/detailed`
- **Purpose**: Comprehensive component health status
- **Method**: GET
- **Response**: JSON with detailed component status
- **HTTP Status Codes**:
  - 200: All components healthy or some degraded
  - 503: One or more components unhealthy
  
Example response:
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2024-01-18T10:30:00",
  "uptime_seconds": 3600,
  "uptime_human": "1h",
  "components": [
    {
      "name": "database",
      "status": "healthy",
      "message": "Database connection OK, 1523 vehicles",
      "response_time_ms": 15.23,
      "checked_at": "2024-01-18T10:30:00"
    },
    {
      "name": "cache",
      "status": "degraded",
      "message": "Cache disabled, using fallback",
      "checked_at": "2024-01-18T10:30:00"
    },
    {
      "name": "eBay Motors API",
      "status": "healthy",
      "message": "API endpoint reachable, status: 200",
      "response_time_ms": 234.56,
      "checked_at": "2024-01-18T10:30:00"
    }
  ],
  "metrics": {
    "response_times": {
      "avg": 125.5,
      "p50": 110.0,
      "p95": 250.0,
      "p99": 500.0
    },
    "error_rate": 0.02,
    "cache_hit_rate": 0.85,
    "api_performance": {
      "ebay": {
        "avg_duration": 0.234,
        "success_rate": 0.98,
        "total_calls": 150
      }
    }
  }
}
```

### 3. Prometheus Metrics - `/metrics`
- **Purpose**: Export metrics in Prometheus format for monitoring systems
- **Method**: GET
- **Response**: Plain text in Prometheus exposition format
- **Content-Type**: `text/plain; version=0.0.4`

Example output:
```
# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds summary
http_request_duration_seconds_avg 0.125
http_request_duration_seconds_p50 0.110
http_request_duration_seconds_p95 0.250
http_request_duration_seconds_p99 0.500
http_request_duration_seconds_count 1523

# HELP cache_hit_rate Cache hit rate
# TYPE cache_hit_rate gauge
cache_hit_rate 0.850

# HELP database_query_duration_seconds Database query duration
# TYPE database_query_duration_seconds gauge
database_query_duration_seconds 0.015
```

### 4. Health Dashboard - `/health/dashboard`
- **Purpose**: Visual health monitoring dashboard
- **Method**: GET
- **Response**: 
  - HTML dashboard (default)
  - JSON data (with `Accept: application/json` header)
  
The dashboard provides:
- Overall system status with visual indicators
- Key performance metrics
- Component health status
- API performance statistics
- Response time distribution
- Auto-refresh every 30 seconds

## Monitored Components

### 1. Database
- Connection health
- Query performance
- Active connections
- Total vehicle count

### 2. Cache System
- Redis availability
- Cache hit/miss rates
- Fallback status
- Total keys

### 3. External APIs
- eBay Motors API
- CarMax API (placeholder)
- AutoTrader API (placeholder)
- Response times
- Success rates

### 4. Application Metrics
- Request response times (avg, p50, p95, p99)
- Error rates by type
- Cache performance
- API call statistics

## Performance Tracking

The health monitor automatically tracks:
- **Response Times**: For all endpoints (excluding static files)
- **Error Rates**: Categorized by error type
- **Database Queries**: Type and duration
- **Cache Operations**: Hits and misses
- **External API Calls**: Duration and success rate

## Integration with Monitoring Systems

### Prometheus/Grafana
1. Configure Prometheus to scrape `/metrics` endpoint
2. Import provided Grafana dashboards
3. Set up alerts based on metrics

### Example Prometheus Configuration
```yaml
scrape_configs:
  - job_name: 'findmycar'
    static_configs:
      - targets: ['localhost:8603']
    scrape_interval: 30s
```

### Health Check Integration
- Load balancers: Use `/health` for basic checks
- Kubernetes: Configure liveness/readiness probes
- Monitoring services: Use `/health/detailed` for comprehensive checks

## Alerting Thresholds

Recommended alert configurations:
- **Response Time**: Alert if p95 > 1s for 5 minutes
- **Error Rate**: Alert if > 5% for 5 minutes
- **Database**: Alert if unhealthy for 2 minutes
- **Cache Hit Rate**: Alert if < 50% for 10 minutes
- **API Success Rate**: Alert if < 90% for 5 minutes

## Usage Examples

### Check System Health
```bash
# Basic health check
curl http://localhost:8603/health

# Detailed health status
curl http://localhost:8603/health/detailed

# Get Prometheus metrics
curl http://localhost:8603/metrics

# View health dashboard
open http://localhost:8603/health/dashboard
```

### Monitor with Python
```python
import requests

# Get detailed health status
response = requests.get('http://localhost:8603/health/detailed')
health_data = response.json()

if health_data['status'] == 'unhealthy':
    print("System is unhealthy!")
    for component in health_data['components']:
        if component['status'] == 'unhealthy':
            print(f"- {component['name']}: {component['message']}")
```

## Troubleshooting

### Common Issues

1. **All APIs showing as unhealthy**
   - Check network connectivity
   - Verify API credentials are configured
   - Check firewall rules

2. **High error rates**
   - Check application logs
   - Review recent deployments
   - Verify database connectivity

3. **Low cache hit rates**
   - Check Redis availability
   - Review cache key strategies
   - Verify TTL settings

4. **Slow response times**
   - Check database query performance
   - Review external API latencies
   - Monitor server resources

## Future Enhancements

1. **Custom Metrics**
   - Business metrics (searches/minute, conversions)
   - Feature-specific monitoring
   - User experience metrics

2. **Advanced Monitoring**
   - Distributed tracing integration
   - Log aggregation correlation
   - Anomaly detection

3. **Automation**
   - Auto-scaling based on metrics
   - Self-healing capabilities
   - Predictive alerting