#!/usr/bin/env python3
"""
Generate a secure secret key for the application
"""
import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    # Remove problematic characters for shell commands
    safe_chars = alphabet.replace('"', '').replace("'", '').replace('\\', '').replace('`', '')
    return ''.join(secrets.choice(safe_chars) for _ in range(length))

if __name__ == "__main__":
    secret_key = generate_secret_key(32)
    print("🔐 Generated Secret Key:")
    print("=" * 50)
    print(secret_key)
    print("=" * 50)
    print("\n📋 To create the secret in Google Cloud:")
    print(f'echo -n "{secret_key}" | gcloud secrets create app-secret-key --data-file=-')
    print("\n⚠️  Save this key securely - you won't be able to retrieve it later!")