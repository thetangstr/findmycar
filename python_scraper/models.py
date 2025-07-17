import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# --- Configuration ---
SERVICE_ACCOUNT_KEY_PATH = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
CARS_COLLECTION = 'cars'

DB_CLIENT = None
_firebase_app_initialized = False

def initialize_firebase_app():
    """
    Initializes the Firebase Admin SDK and returns a Firestore client.
    Handles initialization only once and provides verbose logging.
    """
    global DB_CLIENT, _firebase_app_initialized
    if DB_CLIENT:
        return DB_CLIENT

    if not _firebase_app_initialized:
        try:
            print("Attempting to initialize Firebase App...")
            cred = None
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                print("Using GOOGLE_APPLICATION_CREDENTIALS.")
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            elif os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
                print(f"Using service account key from: {SERVICE_ACCOUNT_KEY_PATH}")
                cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
                firebase_admin.initialize_app(cred)
            else:
                print("Using default credentials. Ensure gcloud auth is configured.")
                firebase_admin.initialize_app()
            
            print("Firebase App initialized successfully.")
            _firebase_app_initialized = True

        except ValueError as e:
            if 'The default Firebase app already exists' in str(e):
                print("Firebase app was already initialized.")
                _firebase_app_initialized = True
            else:
                print(f"A ValueError occurred during Firebase app initialization: {e}")
                return None
        except Exception as e:
            print(f"A general error occurred during Firebase app initialization: {e}")
            return None

    try:
        print("Attempting to get Firestore client...")
        DB_CLIENT = firestore.client()
        print("Firestore client obtained successfully.")
        return DB_CLIENT
    except Exception as e:
        print(f"Error getting Firestore client: {e}")
        DB_CLIENT = None
        return None

def add_car_listing(db, car_data):
    """
    Adds a car listing to the Firestore database.
    Checks for duplicates based on 'listing_url'.
    """
    if not db:
        print("Firestore client not available. Cannot add car listing.")
        return None

    listing_url = car_data.get('listing_url')
    if not listing_url:
        print("Error: listing_url is required to add a car.")
        return None

    try:
        collection_ref = db.collection(CARS_COLLECTION)
        query = collection_ref.where('listing_url', '==', listing_url).limit(1).stream()
        
        existing_docs = list(query)
        
        if existing_docs:
            doc_ref = existing_docs[0].reference
            print(f"Duplicate found for {listing_url}. Updating last_seen_at.")
            doc_ref.update({'last_seen_at': datetime.utcnow()})
            return doc_ref.id
        else:
            print(f"No duplicate found. Adding new listing for {listing_url}.")
            car_data['scraped_at'] = datetime.utcnow()
            car_data['last_seen_at'] = datetime.utcnow()
            update_time, doc_ref = collection_ref.add(car_data)
            print(f"Successfully added new listing with ID: {doc_ref.id}")
            return doc_ref.id
    except Exception as e:
        print(f"An error occurred while adding car listing to Firestore: {e}")
        return None

# --- Car Data Structure (for reference) ---
# Each car document in the 'cars' collection will ideally have:
# {
#   'source': str,          # e.g., "Hemmings"
#   'listing_url': str,     # Unique URL, used as document ID or for duplicate checks
#   'title': str,
#   'price': int,           # Store as integer (e.g., 25000 for $25,000)
#   'year': int,
#   'make': str,
#   'model': str,
#   'mileage': int,         # Optional, store if available
#   'location': str,
#   'image_urls': list[str], # List of image URLs
#   'description': str,     # Optional, if available from scraper
#   'raw_details': dict,    # Optional, to store any other key-value details from structured data
#   'scraped_at': datetime, # Firestore Timestamp of when it was scraped
#   'last_seen_at': datetime # Firestore Timestamp, updated if listing is seen again
# }

    db = initialize_firebase_app()
    if not db:
        print("Firestore client not available. Cannot add car listing.")
        return None

    listing_url = car_data.get('listing_url')
    if not listing_url:
        print("Error: listing_url is required to add a car.")
        return None

    # Use listing_url (sanitized) as document ID or check for existing doc with this URL
    # For simplicity, let's query first to avoid overwriting if we don't use URL as ID.
    # A more robust way for high-volume writes might be to use listing_url (hashed/sanitized) as doc ID.
    
    collection_ref = db.collection(CARS_COLLECTION)
    query = collection_ref.where('listing_url', '==', listing_url).limit(1).stream()
    
    existing_docs = list(query)
    if existing_docs:
        print(f"Listing already exists for URL: {listing_url}. Updating last_seen_at.")
        doc_ref = existing_docs[0].reference
        doc_ref.update({'last_seen_at': datetime.utcnow()})
        return doc_ref.id
    else:
        # Add new listing
        car_data['scraped_at'] = datetime.utcnow()
        car_data['last_seen_at'] = datetime.utcnow()
        doc_ref = collection_ref.add(car_data)
        print(f"Added new listing: {listing_url} with ID: {doc_ref[1].id}")
        return doc_ref[1].id # add() returns a tuple (timestamp, DocumentReference)

if __name__ == '__main__':
    # Example usage (for testing models.py directly)
    # Ensure your SERVICE_ACCOUNT_KEY_PATH is set correctly or GOOGLE_APPLICATION_CREDENTIALS env var.
    print("Attempting to initialize Firebase...")
    db_client = initialize_firebase_app()
    if db_client:
        print("Firebase initialized successfully. Firestore client obtained.")
        # Example: Add a dummy car
        # dummy_car = {
        #     'source': "TestHemmings",
        #     'listing_url': "http://example.com/car/test123unique",
        #     'title': "Test Car Super",
        #     'price': 10000,
        #     'year': 2022,
        #     'make': "TestMake",
        #     'model': "TestModel",
        #     'mileage': 5000,
        #     'location': "Testville, TS",
        #     'image_urls': ["http://example.com/image1.jpg"],
        # }
        # car_id = add_car_listing(dummy_car)
        # if car_id:
        #     print(f"Dummy car processed with ID: {car_id}")
    else:
        print("Failed to initialize Firebase.")
