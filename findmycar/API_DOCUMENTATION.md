# CarGPT API Documentation

## Overview

The CarGPT API provides programmatic access to comprehensive vehicle search functionality, aggregating data from multiple sources including eBay Motors, CarMax, and AutoTrader.

## Authentication

The API supports two authentication methods:

### 1. API Key Authentication (Recommended)

Include your API key in the request header:
```
X-API-Key: fmc_your_api_key_here
```

Or as a query parameter:
```
GET /api/v1/search?api_key=fmc_your_api_key_here&q=Honda
```

### 2. JWT Bearer Token

For session-based authentication:
```
Authorization: Bearer your_jwt_token_here
```

## Getting Started

### 1. Register for API Access

```bash
curl -X POST https://api.cargpt.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "username": "yourusername",
    "password": "securepassword"
  }'
```

Response:
```json
{
  "success": true,
  "user_id": 123,
  "api_key": "fmc_abcd1234...",
  "message": "Save your API key securely. It cannot be retrieved later."
}
```

### 2. Make Your First Request

```bash
curl https://api.cargpt.com/api/v1/search \
  -H "X-API-Key: fmc_your_api_key" \
  -G -d "q=Honda+Civic"
```

## API Endpoints

### Public Endpoints (No Authentication Required)

#### GET /api/public/search
Limited vehicle search (max 5 results).

**Parameters:**
- `q` (string): Search query

**Example:**
```bash
curl https://api.cargpt.com/api/public/search?q=Toyota
```

### Authenticated Endpoints

#### GET /api/v1/search
Full vehicle search with live data from multiple sources.

**Parameters:**
- `q` (string): Search query
- `make` (string): Vehicle make
- `model` (string): Vehicle model
- `year_min` (integer): Minimum year
- `year_max` (integer): Maximum year
- `price_min` (float): Minimum price
- `price_max` (float): Maximum price
- `mileage_max` (integer): Maximum mileage
- `body_style` (string): Body style (sedan, suv, truck, etc.)
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Results per page (max: 100, default: 20)

**Example:**
```bash
curl https://api.cargpt.com/api/v1/search \
  -H "X-API-Key: fmc_your_api_key" \
  -G -d "make=Honda" \
  -d "model=Civic" \
  -d "year_min=2018" \
  -d "price_max=25000"
```

**Response:**
```json
{
  "success": true,
  "vehicles": [
    {
      "id": 1234,
      "listing_id": "ebay_123456",
      "source": "ebay",
      "make": "Honda",
      "model": "Civic",
      "year": 2020,
      "price": 22500,
      "mileage": 25000,
      "location": "Los Angeles, CA",
      "title": "2020 Honda Civic EX - Low Miles",
      "view_item_url": "https://...",
      "image_urls": ["https://..."],
      "is_live": true
    }
  ],
  "total": 156,
  "page": 1,
  "per_page": 20,
  "pages": 8,
  "sources_used": ["local", "ebay", "carmax", "autotrader"],
  "search_time": 2.34,
  "rate_limit": {
    "limit": 1000,
    "remaining": 975
  }
}
```

#### GET /api/v1/vehicle/{vehicle_id}
Get detailed information about a specific vehicle.

**Parameters:**
- `refresh` (boolean): Force refresh from source (default: false)

**Example:**
```bash
curl https://api.cargpt.com/api/v1/vehicle/1234 \
  -H "X-API-Key: fmc_your_api_key"
```

### Authentication Endpoints

#### POST /api/auth/login
Get JWT token for session-based auth.

**Body:**
```json
{
  "username": "yourusername",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /api/auth/refresh-api-key
Generate a new API key (requires JWT authentication).

### Usage & Billing

#### GET /api/usage
Get your current API usage statistics.

**Response (Authenticated):**
```json
{
  "authenticated": true,
  "username": "yourusername",
  "total_requests": 5420,
  "monthly_usage": {
    "2024-01": {
      "requests": 5420,
      "total_response_time": 1234.56
    }
  },
  "rate_limits": {
    "per_minute": 60,
    "per_hour": 1000
  }
}
```

## Rate Limits

| Plan | Requests/Hour | Results/Search | Live Data | Price |
|------|--------------|----------------|-----------|-------|
| Free | 100 | 20 | No | $0 |
| Pro | 1,000 | 100 | Yes | $49/mo |
| Enterprise | Unlimited | Unlimited | Yes | Contact |

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

Error Response Format:
```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "request_id": "req_123456"
}
```

## Best Practices

1. **Cache Results**: To reduce API calls, cache results on your end for frequently searched vehicles.

2. **Use Filters**: Be specific with filters to get more relevant results and reduce response size.

3. **Handle Rate Limits**: Implement exponential backoff when receiving 429 errors.

4. **Batch Requests**: When checking multiple vehicles, use the search endpoint with specific filters rather than individual vehicle requests.

5. **Monitor Usage**: Regularly check your usage to avoid unexpected rate limits.

## Code Examples

### Python
```python
import requests

API_KEY = 'fmc_your_api_key'
BASE_URL = 'https://api.cargpt.com'

# Search for vehicles
response = requests.get(
    f'{BASE_URL}/api/v1/search',
    headers={'X-API-Key': API_KEY},
    params={
        'make': 'Honda',
        'model': 'Civic',
        'year_min': 2018,
        'price_max': 25000
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['total']} vehicles")
    for vehicle in data['vehicles']:
        print(f"{vehicle['year']} {vehicle['make']} {vehicle['model']} - ${vehicle['price']:,}")
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

const API_KEY = 'fmc_your_api_key';
const BASE_URL = 'https://api.cargpt.com';

async function searchVehicles() {
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/search`, {
      headers: { 'X-API-Key': API_KEY },
      params: {
        make: 'Honda',
        model: 'Civic',
        year_min: 2018,
        price_max: 25000
      }
    });
    
    const { data } = response;
    console.log(`Found ${data.total} vehicles`);
    
    data.vehicles.forEach(vehicle => {
      console.log(`${vehicle.year} ${vehicle.make} ${vehicle.model} - $${vehicle.price.toLocaleString()}`);
    });
    
  } catch (error) {
    console.error('API Error:', error.response.data);
  }
}

searchVehicles();
```

### cURL
```bash
# Search with multiple filters
curl "https://api.cargpt.com/api/v1/search" \
  -H "X-API-Key: fmc_your_api_key" \
  -G \
  --data-urlencode "q=Honda Civic" \
  --data-urlencode "year_min=2018" \
  --data-urlencode "price_max=25000" \
  --data-urlencode "mileage_max=50000"

# Get specific vehicle with refresh
curl "https://api.cargpt.com/api/v1/vehicle/1234?refresh=true" \
  -H "X-API-Key: fmc_your_api_key"
```

## Webhooks (Coming Soon)

We're working on webhook support for:
- New vehicles matching saved searches
- Price drops on watched vehicles
- Vehicle status changes (sold, price change, etc.)

## Support

- Email: api-support@cargpt.com
- Documentation: https://docs.cargpt.com
- Status Page: https://status.cargpt.com

## Changelog

### v1.0.0 (Current)
- Initial API release
- Search endpoint with multi-source aggregation
- API key and JWT authentication
- Rate limiting and usage tracking

### Roadmap
- Webhook support
- Saved searches API
- Vehicle history endpoint
- Batch operations
- GraphQL endpoint