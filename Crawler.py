from apify_client import ApifyClient
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import os

# ------------------------------
# Setup
# ------------------------------

# Load environment variables from .env file
load_dotenv()
API_TOKEN = os.getenv("APIFY_API_TOKEN")

if not API_TOKEN:
    raise ValueError("API token not found! Make sure APIFY_API_TOKEN is set in .env")

# Initialize the ApifyClient with API token from .env
client = ApifyClient(API_TOKEN)

# Ask user for the Instagram username
username = input("Enter the Instagram username (without @): ").strip().replace(" ", "")
profile_url = f"https://www.instagram.com/{username}/"

# Calculate the date 6 months ago (ISO format)
six_months_ago = (datetime.utcnow() - timedelta(days=180)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

# Prepare the Actor input
run_input = {
    "directUrls": [profile_url],
    "resultsType": "posts",
    "resultsLimit": 500,
    "onlyPostsNewerThan": six_months_ago,
    "isUserTaggedFeedURL": False,
    "isUserReelFeedURL": False,
    "enhanceUserSearchWithFacebookPage": False,
    "addParentData": False,
}

# Ensure the Extracted_Data folder exists
os.makedirs("Extracted_Data", exist_ok=True)

# Output file path inside Extracted_Data
output_file = os.path.join("Extracted_Data", f"{username}_6months_posts.json")

print(f"🔍 Starting Instagram scrape for @{username} (last 6 months)...")

# ------------------------------
# Run the scraper
# ------------------------------

try:
    # Run the Instagram scraper Actor
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)

    # Collect results
    results = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]

    # Save results to JSON in Extracted_Data
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"✅ Scraping complete for @{username}. Found {len(results)} posts (last 6 months).")
    print(f"📁 Results saved to '{output_file}'")

except Exception as e:
    print(f"❌ Error during scraping: {e}")
