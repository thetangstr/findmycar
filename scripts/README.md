# Bring a Trailer Scraper

This script ethically scrapes vehicle listings from Bring a Trailer (bringatrailer.com) to provide real vehicle data for the FindMyCar application.

## Features

- Respects robots.txt and implements polite scraping practices
- Extracts key vehicle information including title, price, make, model, year, and images
- Converts data to a format compatible with the FindMyCar application
- Implements error handling and logging
- Follows ethical web scraping guidelines

## Requirements

- Python 3.6+
- Required packages: requests, beautifulsoup4

## Installation

1. Install the required packages:

```bash
pip install requests beautifulsoup4
```

## Usage

Run the script from the command line:

```bash
python bat_scraper.py
```

The script will:
1. Check robots.txt to ensure scraping is allowed
2. Fetch the main listings page
3. Extract individual listing URLs
4. Scrape details from each listing
5. Convert the data to the FindMyCar vehicle format
6. Save the results to `src/data/bat_listings.json`

## Ethical Considerations

This scraper:
- Respects the website's robots.txt file
- Implements delays between requests to avoid overloading servers
- Uses a realistic User-Agent string
- Limits the number of requests to minimize server impact
- Only extracts publicly available information

## Integration with FindMyCar

The scraped data is saved in a format compatible with the FindMyCar application and can be used as a source of real vehicle listings. To integrate with the application:

1. Run the scraper to generate the JSON file
2. The FindMyCar application will automatically use this data when available

## Limitations

- The scraper may break if Bring a Trailer changes their website structure
- Some vehicle details may not be available in the listing preview
- The script is intended for development and testing purposes only
