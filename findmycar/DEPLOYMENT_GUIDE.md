# FindMyCar Production Deployment Guide

This guide walks through deploying FindMyCar to a production environment with PostgreSQL, Redis, and Docker.

## Prerequisites

- Docker and Docker Compose installed
- Domain name (optional but recommended)
- SSL certificates (for HTTPS)
- At least 2GB RAM on the server

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd findmycar
```

### 2. Set Up Environment Variables

```bash
# Copy the production environment template
cp .env.prod.example .env.prod

# Edit with your values
nano .env.prod
```

Required variables:
- `POSTGRES_PASSWORD` - Strong password for PostgreSQL
- `REDIS_PASSWORD` - Strong password for Redis
- `EBAY_CLIENT_ID` & `EBAY_CLIENT_SECRET` - Your eBay API credentials
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`

### 3. Deploy with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Initialize Database

The database will be automatically initialized on first run. To manually initialize:

```bash
docker-compose -f docker-compose.prod.yml exec web python init_db.py
```

### 5. Migrate Existing Data (Optional)

If you have existing SQLite data:

```bash
# Set DATABASE_URL for PostgreSQL
export DATABASE_URL=postgresql://findmycar:yourpassword@localhost:5432/findmycar

# Run migration
python migrate_to_postgres.py
```

## Architecture

The production deployment includes:

- **PostgreSQL** - Primary database (port 5432)
- **Redis** - Caching and rate limiting (port 6379)
- **FastAPI** - Application server (2 instances for load balancing)
- **Nginx** - Reverse proxy and load balancer (ports 80/443)
- **Celery** - Background task processing
- **Prometheus & Grafana** - Monitoring (optional)

## Configuration Details

### Database Configuration

The application automatically detects PostgreSQL when `DATABASE_URL` is set. It supports both formats:
- `DATABASE_URL=postgresql://user:pass@host:port/dbname`
- Individual variables: `POSTGRES_HOST`, `POSTGRES_USER`, etc.

### Redis Configuration

Redis is used for:
- API response caching (hot cache)
- Rate limiting
- Session storage
- Background task queue

Falls back to in-memory cache if Redis is unavailable.

### SSL/HTTPS Setup

1. Place your SSL certificates in the `ssl/` directory:
   ```
   ssl/
   ├── cert.pem
   └── key.pem
   ```

2. Update `nginx.conf` with your domain name

3. Restart Nginx:
   ```bash
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

## Scaling

### Horizontal Scaling

Add more application instances:

```yaml
# In docker-compose.prod.yml
app3:
  # Same configuration as app1/app2
```

### Database Optimization

Create indexes for better performance:

```sql
CREATE INDEX idx_vehicles_search ON vehicles(make, model, year);
CREATE INDEX idx_vehicles_price ON vehicles(price);
CREATE INDEX idx_vehicles_location ON vehicles(location);
```

## Monitoring

### Health Checks

- Basic: `http://your-domain/health`
- Detailed: `http://your-domain/health/detailed`

### Grafana Dashboard

Access at `http://your-domain:3000` (default admin password in `.env.prod`)

### Application Metrics

- `/api/stats` - Vehicle statistics
- `/api/popular-searches` - Popular search queries
- `/monitoring` - Real-time monitoring dashboard

## Backup and Recovery

### Database Backup

```bash
# Backup
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U findmycar findmycar > backup.sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U findmycar findmycar < backup.sql
```

### Automated Backups

Add to crontab:
```bash
0 2 * * * /path/to/backup-script.sh
```

## Troubleshooting

### Container Issues

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Restart service
docker-compose -f docker-compose.prod.yml restart [service-name]

# Rebuild containers
docker-compose -f docker-compose.prod.yml build --no-cache
```

### Database Connection Issues

1. Check PostgreSQL is running:
   ```bash
   docker-compose -f docker-compose.prod.yml exec postgres pg_isready
   ```

2. Test connection:
   ```bash
   docker-compose -f docker-compose.prod.yml exec web python -c "from database_config import engine; print(engine.url)"
   ```

### Performance Issues

1. Check Redis connection:
   ```bash
   docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
   ```

2. Monitor resource usage:
   ```bash
   docker stats
   ```

## Security Checklist

- [ ] Strong passwords for PostgreSQL and Redis
- [ ] SECRET_KEY is randomly generated
- [ ] SSL certificates installed
- [ ] Firewall configured (only expose 80/443)
- [ ] Regular security updates
- [ ] Database backups configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured

## Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Database Migrations

When schema changes:
```bash
docker-compose -f docker-compose.prod.yml exec web python init_db.py
```

### Clean Up

```bash
# Remove unused images
docker image prune -a

# Clean logs
docker-compose -f docker-compose.prod.yml exec web truncate -s 0 /app/logs/*.log
```

## Support

For issues or questions:
1. Check application logs
2. Review health check endpoints
3. Consult monitoring dashboards
4. Check GitHub issues