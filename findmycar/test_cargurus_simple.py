#!/usr/bin/env python3
from cargurus_client import search_cargurus_listings
try:
    print('🧪 Testing CarGurus directly...')
    vehicles = search_cargurus_listings('Honda Civic', limit=2)
    print(f'✅ Found {len(vehicles)} vehicles')
    if vehicles:
        print(f'📋 Sample: {vehicles[0]}')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()