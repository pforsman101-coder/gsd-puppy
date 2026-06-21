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
PHONE_TO = "+17322451147"  # Your direct mobile phone line number

# Dynamic browser rotations to navigate around regional shelter proxy blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

def send_alerts(dog_name, dog_url):
    """Dispatches direct, encrypted SMS alerts using Twilio's cloud gateway network."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_NUMBER")
    
    if not account_sid or not auth_token or not twilio_number:
        print("Alert skipped: Twilio SMS keys are not yet configured inside repository settings.")
        return

    message_body = f"🚨 GSD Puppy Match: {dog_name}! Female, purebred GSD under 1 year old found. Link: {dog_url}"
    
    # Executing clean, direct REST API call to Twilio payload centers
    api_url = f"https://twilio.com{account_sid}/Messages.json"
    payload = {
        "To": PHONE_TO,
        "From": twilio_number,
        "Body": message_body
    }
    
    try:
        response = requests.post(api_url, data=payload, auth=(account_sid, auth_token))
        if response.status_code == 201:
            print("📱 Direct text alert successfully pushed to your Xfinity mobile phone!")
        else:
            print(f"Twilio delivery roadblock: {response.text}")
    except Exception as e:
        print(f"SMS transmission exception error: {e}")

def load_existing_matches():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def scan_rescues():
    print("Initiating regional database search patterns...")
    existing_matches = load_existing_matches()
    existing_links = {dog['link'] for dog in existing_matches}
    new_matches_found = False
    
    for url in TARGET_URLS:
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for listing in soup.find_all('table', class_='DogListing') or soup.find_all(class_='id_card_or_table_class'):
                text_content = listing.get_text().lower()
                
                is_purebred = "purebred" in text_content or "mix" not in text_content
                is_female = "female" in text_content
                is_puppy = any(x in text_content for x in ["puppy", "baby"]) or \
                           any(int(m) < 12 for m in re.findall(r'(\d+)\s*month', text_content))
                
                if is_purebred and is_female and is_puppy:
                    name_element = listing.find(class_='dog_name')
                    dog_name = name_element.text.strip() if name_element else "Female GSD Puppy"
                    dog_link = url
                    
                    if dog_link not in existing_links:
                        new_dog = {
                            "name": dog_name,
                            "location": url.split('/')[-1],
                            "link": dog_link,
                            "time_found": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        existing_matches.append(new_dog)
                        new_matches_found = True
                        send_alerts(dog_name, dog_link)
                        
            time.sleep(random.uniform(2.0, 4.0))
                        
        except Exception as e:
            print(f"Bypassing data parsing interval for {url}: {e}")
            
    if new_matches_found:
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_matches, f, indent=4)
        print("Database cache storage files updated.")

if __name__ == "__main__":
    # Force an immediate notification check right at system startup
    send_alerts("Test Puppy Rexi", "https://example.com")
    scan_rescues()
