#!/usr/bin/env python3
"""
Open the new modern UI in the browser
"""

import webbrowser
import time
import requests

# Check if the app is running
try:
    response = requests.get('http://localhost:8601')
    if response.status_code == 200:
        print("✅ FindMyCar app is running on port 8601")
        print("🌐 Opening the new modern UI in your browser...")
        time.sleep(1)
        webbrowser.open('http://localhost:8601')
        print("\n🎉 The new UI should now be open in your browser!")
        print("\nFeatures of the new UI:")
        print("- Clean, modern design similar to the example")
        print("- Prominent AI-powered search box")
        print("- Natural language search queries")
        print("- Featured vehicles section")
        print("- Real-time search across multiple sources")
        print("\nTry searching for:")
        print('- "Family SUV under $25,000"')
        print('- "Fuel efficient sedan for commuting"')
        print('- "Reliable first car under 50k miles"')
    else:
        print("❌ App returned status code:", response.status_code)
        print("Please make sure the Flask app is running on port 8601")
except requests.ConnectionError:
    print("❌ Could not connect to the app on http://localhost:8601")
    print("\nTo start the app, run:")
    print("  python flask_app_production.py")
    print("or")
    print("  ./run_app.sh")