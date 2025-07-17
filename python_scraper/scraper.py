import os
import json
import re
from apify_client import ApifyClient
from bs4 import BeautifulSoup
from models import initialize_firebase_app, add_car_listing

# --- Constants ---
APIFY_API_KEY = os.getenv('APIFY_API_KEY', 'apify_api_NtkoqNJPxcZp01yl7iHjbJPtdM3tg122vbfA')

def fetch_page_with_apify(url):
    """
    Uses the Apify Puppeteer Scraper Actor to fetch the full HTML of a page.
    """
    print(f"Fetching URL via Apify Puppeteer Scraper: {url}")
    if not APIFY_API_KEY:
        print("Error: APIFY_API_KEY environment variable not set.")
        return None

    try:
        client = ApifyClient(APIFY_API_KEY)
        page_function = """
        async function pageFunction({ page, log }) {
            log.info('Waiting 10 seconds for page to load and settle...');
            await new Promise(resolve => setTimeout(resolve, 10000));
            log.info('Extracting page HTML...');
            const html = await page.content();
            return { html };
        }
        """
        run_input = {
            "startUrls": [{ "url": url }],
            "pageFunction": page_function,
            "proxyConfiguration": { "useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"] },
        }
        run = client.actor("apify/puppeteer-scraper").call(run_input=run_input, timeout_secs=120)
        print("Apify actor call finished.")
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"Found {len(items)} items from Apify run.")
        if not items:
            print("Apify actor run finished but returned no items.")
            return None
        html_content = items[0].get('html')
        print(f"HTML content is {'present' if html_content else 'missing'}.")
        return html_content
    except Exception as e:
        print(f"An error occurred while fetching the page with Apify: {e}")
        return None

def parse_car_listing(html_content, url):
    """
    Parses the HTML of a Hemmings car listing page to extract car data.
    """
    if not html_content:
        return None

    print("Parsing car listing details...")
    soup = BeautifulSoup(html_content, 'html.parser')
    car_data = {"listing_url": url, "source": "hemmings"}

    # 1. Extract data from the 'classified-datalayer' script tag
    data_layer_script = soup.find('script', {'id': 'classified-datalayer'})
    if data_layer_script:
        script_content = data_layer_script.string
        if script_content:
            # Use regex to extract values directly from the JS object string
            year_match = re.search(r"listing_v_year:\s*'([^']*)'", script_content)
            make_match = re.search(r"listing_v_make:\s*'([^']*)'", script_content)
            model_match = re.search(r"listing_v_model:\s*'([^']*)'", script_content)
            price_range_match = re.search(r"listing_v_price_range:\s*'([^']*)'", script_content)
            ymm_match = re.search(r"listing_v_ymm:\s*'([^']*)'", script_content)

            if year_match: car_data['year'] = year_match.group(1)
            if make_match: car_data['make'] = make_match.group(1)
            if model_match: car_data['model'] = model_match.group(1)
            if price_range_match: car_data['price_range'] = price_range_match.group(1)
            
            if ymm_match:
                 print(f"Successfully parsed data from dataLayer: {ymm_match.group(1)}")
            else:
                 print("Partially parsed data from dataLayer.")

    # 2. Extract VIN
    vin_dt = soup.find('dt', string=re.compile(r'^\s*VIN #\s*$'))
    if vin_dt:
        vin_dd = vin_dt.find_next_sibling('dd')
        if vin_dd:
            car_data['vin'] = vin_dd.text.strip()
            print(f"Found VIN: {car_data['vin']}")

    # 3. Extract Description
    description_div = soup.find('div', class_='description-text')
    if description_div:
        car_data['description'] = description_div.text.strip()
        print("Found description.")

    # 4. Extract Price
    price_dd = soup.find('dd', class_='price')
    if price_dd:
        price_text = price_dd.text.strip()
        car_data['price'] = price_text
        print(f"Found price: {price_text}")

    return car_data

def main():
    """
    Main function to run the scraper.
    This function will now fetch a search results page and save it for inspection.
    """
    print("--- Starting Hemmings Scraper: Search Page Fetch ---")
    
    # We are now fetching a search results page to find listing URLs.
    search_url = "https://www.hemmings.com/classifieds/cars-for-sale/porsche/911"
    
    print(f"Fetching search results page: {search_url}")
    html_content = fetch_page_with_apify(search_url)
    print(f"Result of fetch_page_with_apify is: {'Content received' if html_content else 'None'}")
    
    if html_content:
        # For debugging, save the fetched HTML to a file to find the listing selectors
        try:
            with open("python_scraper/temp_search_page.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Saved search results HTML to python_scraper/temp_search_page.html for inspection.")
        except Exception as e:
            print(f"Error saving debug HTML file: {e}")
    else:
        print("Failed to fetch search results page HTML. Aborting.")

    print("\n--- Hemmings Scraper Finished ---")

if __name__ == "__main__":
    # We don't need to initialize Firebase for this step, as we are only saving a file.
    main()
