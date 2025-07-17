# CarGPT Production Deployment Guide

## Overview

This guide covers deploying CarGPT to production with full scalability, monitoring, and reliability features including multi-source integration (CarMax, Bring a Trailer).

## Prerequisites

- Docker and Docker Compose
- ChromeDriver for CarMax scraping
- SSL certificates for HTTPS (optional)
- Environment variables configured

## Architecture

The production deployment includes:

- **2x FastAPI app instances** (load balanced)
- **PostgreSQL database** (persistent storage)
- **Redis cache** (caching and Celery broker)
- **Celery worker** (background tasks)
- **Celery beat** (scheduled tasks)
- **Nginx** (load balancer and reverse proxy)
- **Prometheus** (metrics collection)
- **Grafana** (monitoring dashboards)

## Quick Start

### 1. Environment Setup

Copy the example environment file:
```bash
cp .env.prod.example .env.prod
```

Edit `.env.prod` with your actual values:
```bash
# Required - Generate secure passwords
POSTGRES_PASSWORD=your_secure_postgres_password
REDIS_PASSWORD=your_secure_redis_password
SECRET_KEY=your_very_long_random_secret_key

# API Keys
EBAY_CLIENT_ID=your_ebay_client_id
EBAY_CLIENT_SECRET=your_ebay_client_secret
OPENAI_API_KEY=your_openai_api_key
AUTO_DEV_API_KEY=your_autodev_api_key

# Monitoring
GRAFANA_PASSWORD=your_grafana_password
```

### 2. Build and Deploy

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 3. Initialize Database

The database will be automatically initialized with the schema and indexes from `init-db.sql`.

### 4. Access Services

- **Application**: http://localhost (Nginx)
- **API Documentation**: http://localhost/docs
- **Health Check**: http://localhost/health
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/your_grafana_password)

## CarMax Integration

CarMax integration uses Selenium WebDriver for scraping:

### Requirements
- Chrome browser (included in Docker image)
- ChromeDriver (included in Docker image)
- Sufficient memory for browser instances

### Configuration
CarMax scraping is enabled by default. Configure rate limiting and proxy rotation if needed:

```python
# In carmax_client.py
carmax_client = CarMaxClient(
    use_proxy=True,
    proxy_list=['proxy1:port', 'proxy2:port']
)
```

### Monitoring CarMax
- Check logs: `docker logs cargpt-worker`
- Monitor task status via API: `/api/task-status/{task_id}`
- Track scraping success rate in Grafana

## Background Tasks

Celery handles background processing:

### Scheduled Tasks
- **Daily data refresh**: 6 AM UTC (popular searches)
- **Hourly popular searches**: Every hour
- **Weekly valuation updates**: Sunday 3 AM UTC

### Manual Tasks
Start background ingestion:
```bash
curl -X POST "http://localhost/api/background-ingest" \
  -F "query=Honda Civic" \
  -F "sources=ebay,carmax" \
  -F "limit=50"
```

## Monitoring and Alerting

### Health Checks
- Application: `/health`
- Detailed: `/health/detailed`
- Database and cache status included

### Metrics
Prometheus collects metrics on:
- Request rates and response times
- Database connection pool status
- Cache hit/miss rates
- Celery task success/failure rates
- CarMax scraping performance

### Grafana Dashboards
Pre-configured dashboards for:
- Application performance
- Database metrics
- Task queue status
- Error rates and alerts

## Security

### Rate Limiting
Built-in rate limiting per IP:
- API endpoints: 100 requests/hour
- Ingestion: 10 requests/hour
- Search: 5 requests/second

### HTTPS Setup
1. Obtain SSL certificates
2. Place certificates in `./ssl/` directory
3. Uncomment HTTPS section in `nginx.conf`
4. Update domains in nginx configuration

### Security Headers
Nginx automatically adds:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)

## Scaling

### Horizontal Scaling
Add more app instances:
```yaml
# In docker-compose.prod.yml
app3:
  # Same configuration as app1/app2
```

Update nginx upstream block to include new instances.

### Database Scaling
For high traffic:
1. Use PostgreSQL read replicas
2. Implement connection pooling
3. Consider database sharding by source

### Caching Strategy
Redis caching includes:
- Search results (30 minutes)
- Vehicle details (1 hour)
- Vehicle valuations (2 hours)
- API responses (5 minutes)

## Backup and Recovery

### Database Backups
```bash
# Manual backup
docker exec cargpt-postgres pg_dump -U cargpt cargpt > backup.sql

# Automated backup (add to cron)
0 2 * * * docker exec cargpt-postgres pg_dump -U cargpt cargpt | gzip > /backups/cargpt_$(date +%Y%m%d).sql.gz
```

### Redis Persistence
Redis is configured with AOF persistence for data durability.

## Troubleshooting

### Common Issues

**CarMax scraping fails:**
```bash
# Check worker logs
docker logs cargpt-worker

# Check Chrome installation
docker exec cargpt-worker google-chrome --version

# Restart worker if needed
docker-compose -f docker-compose.prod.yml restart worker
```

**High memory usage:**
- CarMax scraping uses Selenium which requires ~200MB per browser instance
- Configure worker concurrency: `--concurrency=2` for limited memory

**Database connection issues:**
```bash
# Check PostgreSQL status
docker logs cargpt-postgres

# Test connection
docker exec cargpt-postgres psql -U cargpt -c "SELECT 1"
```

### Performance Tuning

**Database:**
- Adjust PostgreSQL `shared_buffers` and `work_mem`
- Monitor query performance with `pg_stat_statements`
- Add indexes for frequently searched fields

**Application:**
- Increase worker processes: `--workers 4`
- Tune database connection pool size
- Implement query result caching

**CarMax Scraping:**
- Implement proxy rotation for large-scale scraping
- Add delays between requests: 2-5 seconds
- Monitor for IP blocking and implement retry logic

## Maintenance

### Updates
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Log Rotation
Configure log rotation for:
- Application logs in `./logs/`
- Docker container logs
- Nginx access logs

### Health Monitoring
Regular checks:
- Application health endpoints
- Database connection status
- Cache performance metrics
- Task queue length and success rates

## Cost Optimization

### Resource Allocation
- **Minimum**: 2 CPU cores, 4GB RAM
- **Recommended**: 4 CPU cores, 8GB RAM
- **High traffic**: 8+ CPU cores, 16GB+ RAM

### Service Optimization
- Use smaller Docker images for faster deployments
- Implement efficient caching to reduce database load
- Optimize Selenium usage to minimize memory consumption
- Configure appropriate worker concurrency based on available resources

This production setup provides a robust, scalable platform for CarGPT with comprehensive multi-source integration (CarMax, Bring a Trailer) and monitoring capabilities.