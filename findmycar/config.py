from dotenv import load_dotenv
import os
import base64

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

# eBay API credentials
EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID", "KailorTa-fmc-PRD-a8e70e47c-c916c494")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET", "PRD-8e70e47c45e6-8603-4564-9283-bd68")

# Create base64 encoded credentials for OAuth
credentials = f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}"
EBAY_API_KEY = base64.b64encode(credentials.encode()).decode()

# Backward compatibility
EBAY_APP_ID = EBAY_CLIENT_ID

# OpenAI API key for natural language processing
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
