#!/usr/bin/env python3
"""Test the backend logic for price and mileage filtering."""

from nlp_search import parse_natural_language_query

def test_backend_logic(query, price_min_form=5000, price_max_form=100000, max_mileage_form=None):
    """Simulate what the backend does."""
    # Parse natural language query
    nlp_filters = parse_natural_language_query(query)
    
    # Backend logic for price
    query_lower = query.lower()
    has_price_terms = any(term in query_lower for term in ['$', 'price', 'cost', 'under', 'over', 'below', 'above', 'cheap', 'expensive', 'budget', 'max', 'maximum', 'min', 'minimum'])
    
    if has_price_terms:
        # Query mentions price, use NLP results only (even if None)
        price_min = nlp_filters.get('price_min')
        price_max = nlp_filters.get('price_max')
    else:
        # Query doesn't mention price, use form defaults only if not default values
        price_min = price_min_form if price_min_form and price_min_form != 5000 else None
        price_max = price_max_form if price_max_form and price_max_form != 100000 else None
    
    # Backend logic for mileage
    has_mileage_terms = any(term in query_lower for term in ['miles', 'mileage', 'high mileage', 'low mileage', 'km', 'kilometers'])
    
    if has_mileage_terms:
        # Query mentions mileage, use NLP results only (even if None)
        mileage_min = nlp_filters.get('mileage_min')
        mileage_max = nlp_filters.get('mileage_max')
    else:
        # Query doesn't mention mileage, use form values only if provided
        mileage_min = None
        mileage_max = max_mileage_form if max_mileage_form else None
    
    return {
        'price_min': price_min,
        'price_max': price_max,
        'mileage_min': mileage_min,
        'mileage_max': mileage_max,
        'has_price_terms': has_price_terms,
        'has_mileage_terms': has_mileage_terms
    }

if __name__ == "__main__":
    # Test cases
    test_cases = [
        ('honda civic eg6', 5000, 100000, None),  # No price/mileage in query
        ('honda civic under $15k', 5000, 100000, None),  # Price in query
        ('honda civic under 50k miles', 5000, 100000, None),  # Mileage in query
        ('honda civic', 10000, 80000, 120000),  # No price/mileage, custom form values
        ('honda civic high mileage', 5000, 100000, None),  # High mileage
        ('honda civic low mileage', 5000, 100000, None),  # Low mileage
    ]

    for query, price_min_form, price_max_form, max_mileage_form in test_cases:
        result = test_backend_logic(query, price_min_form, price_max_form, max_mileage_form)
        print(f'Query: {query}')
        print(f'  Form: price_min={price_min_form}, price_max={price_max_form}, max_mileage={max_mileage_form}')
        print(f'  Result: price_min={result["price_min"]}, price_max={result["price_max"]}, mileage_min={result["mileage_min"]}, mileage_max={result["mileage_max"]}')
        print(f'  Has price terms: {result["has_price_terms"]}, Has mileage terms: {result["has_mileage_terms"]}')
        print()