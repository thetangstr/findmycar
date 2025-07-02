import os
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from functools import wraps
from config import EBAY_API_KEY
from rate_limiter import ebay_rate_limiter

# Configure logging
logger = logging.getLogger(__name__)

# Token cache
_token_cache = {
    'token': None,
    'expires_at': None
}

class EbayAPIError(Exception):
    """Custom exception for eBay API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class RateLimitError(EbayAPIError):
    """Raised when API rate limit is exceeded"""
    pass

def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for retrying failed requests with exponential backoff
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, EbayAPIError) as e:
                    last_exception = e
                    
                    # Don't retry on 4xx errors (except 429)
                    if isinstance(e, EbayAPIError) and e.status_code and 400 <= e.status_code < 500:
                        if e.status_code != 429:  # Don't retry client errors except rate limit
                            raise
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"Request failed after {max_retries} attempts: {str(e)}")
                        raise
            
            raise last_exception
        return wrapper
    return decorator

def get_ebay_oauth_token(force_refresh: bool = False) -> str:
    """
    Get OAuth token for eBay API access with caching.
    
    Args:
        force_refresh: Force refresh token even if cached token is valid
        
    Returns:
        OAuth access token
        
    Raises:
        EbayAPIError: If token acquisition fails
    """
    # Check cache first
    if not force_refresh and _token_cache['token'] and _token_cache['expires_at']:
        if datetime.now() < _token_cache['expires_at']:
            logger.debug("Using cached OAuth token")
            return _token_cache['token']
    
    logger.info("Acquiring new OAuth token")
    
    # Apply rate limiting
    wait_time = ebay_rate_limiter.wait_and_acquire('oauth')
    if wait_time > 0:
        logger.info(f"Rate limited, waited {wait_time:.2f}s")
    
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {EBAY_API_KEY}'
    }
    
    data = {
        'grant_type': 'client_credentials',
        'scope': 'https://api.ebay.com/oauth/api_scope'
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
        
        if not token:
            raise EbayAPIError("No access token in response")
        
        # Cache token with expiration (subtract 60 seconds for safety)
        _token_cache['token'] = token
        _token_cache['expires_at'] = datetime.now() + timedelta(seconds=expires_in - 60)
        
        logger.info("OAuth token acquired successfully")
        return token
        
    except requests.exceptions.Timeout:
        raise EbayAPIError("OAuth token request timed out")
    except requests.exceptions.RequestException as e:
        raise EbayAPIError(f"OAuth token request failed: {str(e)}")
    except Exception as e:
        raise EbayAPIError(f"Failed to get OAuth token: {str(e)}")

@retry_with_backoff(max_retries=3)
def search_ebay_listings(
    query: str, 
    filters: Optional[Dict[str, Any]] = None, 
    limit: int = 25, 
    offset: int = 0
) -> Dict[str, Any]:
    """
    Searches for car listings on eBay Motors using Browse API.
    
    Args:
        query: Search query string
        filters: Optional filters (make, model, year_min, year_max, price_min, price_max)
        limit: Number of results to return (max 200)
        offset: Pagination offset
        
    Returns:
        Dict containing itemSummaries list and total count
        
    Raises:
        EbayAPIError: If API request fails
        RateLimitError: If rate limit is exceeded
    """
    if not query:
        raise ValueError("Search query cannot be empty")
    
    if limit > 200:
        limit = 200
        logger.warning("Limit exceeds maximum, capping at 200")
    
    # Apply rate limiting
    wait_time = ebay_rate_limiter.wait_and_acquire('search')
    if wait_time > 0:
        logger.info(f"Rate limited, waited {wait_time:.2f}s")
    
    token = get_ebay_oauth_token()
    
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
    }
    
    # Build search parameters
    params = {
        'q': query,
        'category_ids': '6001',  # Cars & Trucks category
        'limit': limit,
        'offset': offset,
        'sort': 'price',
        'filter': 'buyingOptions:{FIXED_PRICE},itemLocationCountry:US,price:[1000..100000]'
    }
    
    # Add additional filters if provided
    if filters:
        additional_filters = []
        
        if filters.get('make'):
            additional_filters.append(f"aspects:Make:{filters['make']}")
        if filters.get('model'):
            additional_filters.append(f"aspects:Model:{filters['model']}")
        if filters.get('year_min') and filters.get('year_max'):
            additional_filters.append(f"aspects:Year:[{filters['year_min']}..{filters['year_max']}]")
        
        # Update price filter if custom range provided
        if filters.get('price_min') and filters.get('price_max'):
            params['filter'] = params['filter'].replace(
                '[1000..100000]', 
                f"[{filters['price_min']}..{filters['price_max']}]"
            )
        
        if additional_filters:
            params['filter'] += ',' + ','.join(additional_filters)
    
    try:
        logger.info(f"Searching eBay with query: {query}, offset: {offset}")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            items = data.get('itemSummaries', [])
            logger.info(f"Search returned {len(items)} items (total: {total})")
            
            return {
                'items': items,
                'total': total,
                'offset': offset,
                'limit': limit
            }
        
        elif response.status_code == 401:
            # Token might be expired, try once with fresh token
            logger.warning("Got 401, refreshing token and retrying")
            token = get_ebay_oauth_token(force_refresh=True)
            headers['Authorization'] = f'Bearer {token}'
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'items': data.get('itemSummaries', []),
                    'total': data.get('total', 0),
                    'offset': offset,
                    'limit': limit
                }
            
        elif response.status_code == 429:
            # Rate limit exceeded
            retry_after = response.headers.get('Retry-After', '60')
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {retry_after} seconds",
                status_code=429,
                response_data={'retry_after': retry_after}
            )
        
        # Handle other errors
        error_data = {}
        try:
            error_data = response.json()
        except:
            pass
        
        raise EbayAPIError(
            f"eBay API Error: {response.status_code} - {response.text}",
            status_code=response.status_code,
            response_data=error_data
        )
        
    except requests.exceptions.Timeout:
        raise EbayAPIError("Search request timed out")
    except requests.exceptions.RequestException as e:
        raise EbayAPIError(f"Search request failed: {str(e)}")

@retry_with_backoff(max_retries=3)
def get_item_details(item_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information for a specific eBay item.
    
    Args:
        item_id: eBay item ID
        
    Returns:
        Item details dict or None if not found
        
    Raises:
        EbayAPIError: If API request fails
    """
    if not item_id:
        raise ValueError("Item ID cannot be empty")
    
    # Apply rate limiting
    wait_time = ebay_rate_limiter.wait_and_acquire('get_item')
    if wait_time > 0:
        logger.info(f"Rate limited, waited {wait_time:.2f}s")
    
    token = get_ebay_oauth_token()
    
    # Handle different item ID formats
    if '|' in item_id:
        # Already in correct format
        formatted_id = item_id
    else:
        # Legacy numeric ID, may need conversion
        formatted_id = item_id
    
    url = f"https://api.ebay.com/buy/browse/v1/item/{formatted_id}"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
    }
    
    try:
        logger.info(f"Getting details for item: {item_id}")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        
        elif response.status_code == 401:
            # Token might be expired, try once with fresh token
            logger.warning("Got 401, refreshing token and retrying")
            token = get_ebay_oauth_token(force_refresh=True)
            headers['Authorization'] = f'Bearer {token}'
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
        
        elif response.status_code == 404:
            logger.warning(f"Item not found: {item_id}")
            return None
        
        elif response.status_code == 429:
            # Rate limit exceeded
            retry_after = response.headers.get('Retry-After', '60')
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {retry_after} seconds",
                status_code=429,
                response_data={'retry_after': retry_after}
            )
        
        # Handle other errors
        error_data = {}
        try:
            error_data = response.json()
        except:
            pass
        
        raise EbayAPIError(
            f"eBay Item Details Error: {response.status_code} - {response.text}",
            status_code=response.status_code,
            response_data=error_data
        )
        
    except requests.exceptions.Timeout:
        raise EbayAPIError("Item details request timed out")
    except requests.exceptions.RequestException as e:
        raise EbayAPIError(f"Item details request failed: {str(e)}")

def clear_token_cache():
    """Clear the cached OAuth token"""
    _token_cache['token'] = None
    _token_cache['expires_at'] = None
    logger.info("Token cache cleared")

def get_rate_limit_status() -> Dict[str, Any]:
    """
    Get current rate limit status for all operations.
    
    Returns:
        Dict with remaining calls and daily limits
    """
    return {
        'search': {
            'remaining': ebay_rate_limiter.get_remaining_calls('search'),
            'daily_limit': ebay_rate_limiter.daily_limits['search']
        },
        'get_item': {
            'remaining': ebay_rate_limiter.get_remaining_calls('get_item'),
            'daily_limit': ebay_rate_limiter.daily_limits['get_item']
        },
        'oauth': {
            'remaining': ebay_rate_limiter.get_remaining_calls('oauth'),
            'daily_limit': ebay_rate_limiter.daily_limits['oauth']
        }
    }