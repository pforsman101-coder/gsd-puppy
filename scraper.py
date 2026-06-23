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
    """Dispatches direct SMS alerts using Twilio's gateway network."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_NUMBER")
    
    if not account_sid or not auth_token or not twilio_number:
        print("Alert skipped: Twilio keys missing.")
        return

    message_body = f"🚨 GSD Puppy Match: {dog_name}! Female GSD under 1 year old found. Link: {dog_url}"
    api_url = f"https://twilio.com{account_sid}/Messages.json"
    payload = {"To": PHONE_TO, "From": twilio_number, "Body": message_body}
    
    try:
        requests.post(api_url, data=payload, auth=(account_sid, auth_token))
        print(f"📱 Direct text alert successfully pushed for {dog_name}!")
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
    print("🚀 Initiating explicit regional deep-block search loops...")
    existing_matches = load_existing_matches()
    existing_links = {dog['link'] for dog in existing_matches}
    new_matches_found = False
    
    for url in TARGET_URLS:
        print(f"🕵️ Scanning region layout strings for: {url}")
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract independent listings by capturing tabular profile rows
            listings = soup.find_all('table') + soup.find_all('div', style=True)
            
            for item in listings:
                text_content = item.get_text().lower()
                if not text_content or len(text_content.strip()) < 40:
                    continue
                
                # Rigid filter parameters targeting Shepherd layouts explicitly
                is_gsd = "shepherd" in text_content or "gsd" in text_content
                is_female = "female" in text_content or "(f)" in text_content
                is_puppy = any(x in text_content for x in ["puppy", "baby", "weeks", "6 month", "8 month", "young"])
                
                if is_gsd and is_female and is_puppy:
                    # Target link element anchors directly
                    link_element = item.find('a', href=True)
                    
                    if link_element and link_element.text.strip():
                        clean_name = link_element.text.strip()
                    else:
                        clean_name = "German Shepherd Puppy"
                    
                    # Generate a unique profile index key using string hashes
                    unique_link = f"{url}#id_{abs(hash(text_content[:60]))}"
                    
                    if unique_link not in existing_links:
                        new_dog = {
                            "name": clean_name,
                            "location": url.split('/')[-1].capitalize(),
                            "link": unique_link,
                            "time_found": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        existing_matches.append(new_dog)
                        existing_links.add(unique_link)
                        new_matches_found = True
                        send_alerts(clean_name, url)
                        
            time.sleep(random.uniform(2.0, 3.5))
                        
        except Exception as e:
            print(f"   ⚠️ Block parsing error: {e}")
            
    if new_matches_found:
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_matches, f, indent=4)
        print("Database array completely updated with fresh puppy datasets.")
    else:
        print("No new matching puppy entries logged.")

if __name__ == "__main__":
    scan_rescues()
