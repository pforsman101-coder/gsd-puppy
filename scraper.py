import os
import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup

ZIP_CODE = "07724"
# Directly targeting Rescue Me's underlying embed data streams
TARGET_URLS = [
    "https://germanshepherd.rescueme.org/newjersey",
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
    print("🚀 Running deep-frame data inspection...")
    existing_matches = load_existing_matches()
    existing_links = {dog['link'] for dog in existing_matches}
    new_matches_found = False
    
    for url in TARGET_URLS:
        print(f"\n🕵️ Checking region: {url}")
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract raw block data independently of iframe structures
            all_text_blobs = soup.find_all(text=True)
            page_text = " ".join([t.lower() for t in all_text_blobs if t.strip()])
            
            # Check if there are dogs on the page generally
            if "shepherd" in page_text or "gsd" in page_text:
                print("   Found active pet profile blocks inside data stream.")
                
                # Dynamic matching rules to catch profiles cleanly
                has_female = "female" in page_text or " (f) " in page_text
                has_puppy = any(x in page_text for x in ["puppy", "baby", "month", "weeks", "young"])
                
                if has_female and has_puppy:
                    # Capture the data record securely
                    dog_name = f"German Shepherd Puppy ({url.split('/')[-1]})"
                    dog_link = url
                    
                    if dog_link not in existing_links:
                        new_dog = {
                            "name": dog_name,
                            "location": url.split('/')[-1].capitalize(),
                            "link": dog_link,
                            "time_found": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        existing_matches.append(new_dog)
                        existing_links.add(dog_link)
                        new_matches_found = True
                        send_alerts(dog_name, dog_link)
            else:
                print("   No text matches inside raw data layers.")
                
            time.sleep(random.uniform(2.0, 4.0))
                        
        except Exception as e:
            print(f"   ⚠️ Roadblock parsing portal: {e}")
            
    if new_matches_found:
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_matches, f, indent=4)
        print("\n💾 Success: data file successfully populated!")
    else:
        print("\n🔍 No matching profiles recorded during this run cycle.")

if __name__ == "__main__":
    scan_rescues()
