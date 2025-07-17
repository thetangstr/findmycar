from nlp_search import parse_natural_language_query

# Test EG6 parsing
query = "honda civic eg6"
result = parse_natural_language_query(query)

print(f"Query: {query}")
print(f"Make: {result.get('make')}")
print(f"Model: {result.get('model')}")
print(f"Year Min: {result.get('year_min')}")
print(f"Year Max: {result.get('year_max')}")
print(f"Chassis Code: {result.get('chassis_code')}")