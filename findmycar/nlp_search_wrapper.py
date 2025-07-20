"""
Wrapper class for NLP search parser
"""

from nlp_search import parse_natural_language_query

class NLPSearchParser:
    """Wrapper class for the NLP search parser function"""
    
    def parse_natural_language_query(self, query: str):
        """Parse natural language query using the existing function"""
        return parse_natural_language_query(query)