#!/usr/bin/env python3
"""
Debug environment variables loading
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("Environment Debug Script")
print("="*50)

# Show current working directory
print(f"Current directory: {os.getcwd()}")

# Check if .env file exists
env_path = Path('.env')
print(f"\n.env file exists: {env_path.exists()}")
print(f".env file path: {env_path.absolute()}")

# Try loading .env
print("\nLoading .env file...")
load_dotenv()

# Check for keys
keys_to_check = [
    'EBAY_CLIENT_ID',
    'MARKETCHECK_API_KEY',
    'AUTOWEB_PARTNER_ID',
    'CARSDIRECT_AFFILIATE_ID'
]

print("\nEnvironment variables:")
for key in keys_to_check:
    value = os.getenv(key)
    if value:
        # Show first 8 chars for security
        display_value = f"{value[:8]}..." if len(value) > 8 else value
        print(f"  {key}: {display_value}")
    else:
        print(f"  {key}: Not found")

# Also check if it's in os.environ directly
print("\nChecking os.environ directly:")
marketcheck_in_environ = 'MARKETCHECK_API_KEY' in os.environ
print(f"  MARKETCHECK_API_KEY in os.environ: {marketcheck_in_environ}")

# Try reading .env file directly
print("\nReading .env file directly:")
if env_path.exists():
    with open('.env', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'MARKETCHECK' in line:
                # Don't show the actual value
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    print(f"  Found: {parts[0]}=...")
                else:
                    print(f"  Found line with MARKETCHECK: {line.strip()[:30]}...")