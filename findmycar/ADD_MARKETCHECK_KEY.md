# How to Add Marketcheck API Key

## Steps:

1. Open the `.env` file in your editor

2. Add this line at the end:
```
MARKETCHECK_API_KEY=your_actual_marketcheck_api_key_here
```

3. Save the file

## Getting a Marketcheck API Key:

1. Go to https://www.marketcheck.com/apis
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key
5. Replace `your_actual_marketcheck_api_key_here` with your actual key

## Verify it's working:

After adding the key, run:
```bash
python test_marketcheck.py
```

This will test the Cars.com integration through Marketcheck API.