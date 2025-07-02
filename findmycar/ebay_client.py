
import os
import requests
from config import EBAY_API_KEY

def get_ebay_oauth_token():
    """
    Get OAuth token for eBay API access.
    """
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {EBAY_API_KEY}'  # Base64 encoded client_id:client_secret
    }
    
    data = {
        'grant_type': 'client_credentials',
        'scope': 'https://api.ebay.com/oauth/api_scope'
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Failed to get OAuth token: {response.status_code}")

def search_ebay_listings(query, filters=None, limit=25, offset=0):
    """
    Searches for car listings on eBay Motors using Browse API.
    """
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
        if filters.get('price_min') and filters.get('price_max'):
            params['filter'] = params['filter'].replace('[1000..100000]', f"[{filters['price_min']}..{filters['price_max']}]")
        
        if additional_filters:
            params['filter'] += ',' + ','.join(additional_filters)
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('itemSummaries', [])
    else:
        print(f"eBay API Error: {response.status_code} - {response.text}")
        return []

def get_item_details(item_id):
    """
    Get detailed information for a specific eBay item.
    """
    token = get_ebay_oauth_token()
    
    url = f"https://api.ebay.com/buy/browse/v1/item/{item_id}"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"eBay Item Details Error: {response.status_code} - {response.text}")
        return None
