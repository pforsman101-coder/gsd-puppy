import os
import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup

ZIP_CODE = "07724"
TARGET_URLS = [
    "https://rescueme.org",
    "https://rescueme.org",
    "https://rescueme.org"
]

JSON_FILE = "listings.json"
PHONE_TO = "+17322451147"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
]

def send_alerts(dog_name, dog_url):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_NUMBER")
    
    if not account_sid or not auth_token or not twilio_number:
        print("Alert skipped: Twilio credentials missing.")
        return

    message_body = f"🚨 GSD Puppy Match: {dog_name}! Female GSD under 1 year old found. Link: {dog_url}"
    api_url = f"https://twilio.com{account_sid}/Messages.json"
    payload = {"To": PHONE_TO, "From": twilio_number, "Body": message_body}
    
    try:
        requests.post(api_url, data=payload, auth=(account_sid, auth_token))
        print(f"📱 Alert sent for {dog_name}!")
    except Exception as e:
        print(f"SMS Error: {e}")

def load_existing_matches():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def scan_rescues():
    print("🚀 Initiating smart global rescue search pattern...")
    existing_matches = load_existing_matches()
    existing_links = {dog['link'] for dog in existing_matches}
    new_matches_found = False
    
    for url in TARGET_URLS:
        print(f"\n🕵️ Fetching live layout data from: {url}")
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # CRITICAL FIX: Extract all block containers dynamically, bypassing class names completely
            containers = soup.find_all(['table', 'div', 'tr'])
            valid_blocks = [c for c in containers if c.get_text() and len(c.get_text().strip()) > 50]
            print(f"   Analyzed {len(valid_blocks)} deep-text website rows.")
            
            match_count_for_url = 0
            for block in valid_blocks:
                text_content = block.get_text().lower()
                
                # Dynamic matching loops to trap variations in website text configurations
                has_breed = "shepherd" in text_content or "gsd" in text_content
                has_gender = "female" in text_content or " (f) " in text_content or " female" in text_content
                has_age = any(x in text_content for x in ["puppy", "baby", "week", "month", "young"])
                
                if has_breed and has_gender and has_age:
                    match_count_for_url += 1
                    
                    # Target bold element patterns or use generic fallback labels
                    bold_text = block.find(['b', 'strong', 'span'])
                    dog_name = bold_text.text.strip() if bold_text else "GSD Female Puppy"
                    dog_name = dog_name.split('\n')[0][:20] # Clean up text string clutter
                    
                    if url not in existing_links:
                        new_dog = {
                            "name": dog_name if len(dog_name) > 2 else "Available GSD Puppy",
                            "location": url.split('/')[-1],
                            "link": url,
                            "time_found": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        existing_matches.append(new_dog)
                        existing_links.add(url)
                        new_matches_found = True
                        send_alerts(dog_name, url)
                        break # Prevent duplication traps within duplicate element blocks
                        
            print(f"   Successfully matched {match_count_for_url} matches against target rules.")
            time.sleep(random.uniform(1.5, 3.0))
                        
        except Exception as e:
            print(f"   ⚠️ Parsing roadblock on regional portal: {e}")
            
    if new_matches_found:
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_matches, f, indent=4)
        print("\n💾 Data file successfully populated and updated!")
    else:
        print("\n🔍 Round complete. No new profiles met strict targets during this run loop.")

if __name__ == "__main__":
    scan_rescues()
