import os
import re
import json
import time
import random
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

ZIP_CODE = "07724"
TARGET_URLS = [
    "https://rescueme.org",
    "https://rescueme.org",
    "https://rescueme.org"
]

JSON_FILE = "listings.json"
EMAIL_TO = "pforsman101@gmail.com"

# Xfinity Mobile routes texts seamlessly through Verizon's SMS gateway
SMS_TARGETS = [
    "7322451147@vtext.com"
]

# Random browsers to bypass data-center scraping blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

def send_alerts(dog_name, dog_url):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        print("Alert skipped: Missing sender configurations.")
        return

    subject = f"🚨 GSD Puppy Match: {dog_name}!"
    body = f"Female purebred GSD under 1 year old found: {dog_name}\nLink: {dog_url}"
    
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = EMAIL_TO
        
        with smtplib.SMTP_SSL("://gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [EMAIL_TO], msg.as_string())
            print("📬 Notification email successfully dispatched.")
            
            for sms_gateway in SMS_TARGETS:
                sms_msg = MIMEText(f"GSD Puppy Alert: {dog_name}! Link: {dog_url}")
                sms_msg['From'] = sender_email
                sms_msg['To'] = sms_gateway
                server.sendmail(sender_email, [sms_gateway], sms_msg.as_string())
            print("📱 Text alert sent to your Xfinity phone.")
    except Exception as e:
        print(f"Alert error: {e}")

def load_existing_matches():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def scan_rescues():
    print("Searching regional GSD networks...")
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
            print(f"Skipping network {url} due to technical connection: {e}")
            
    if new_matches_found:
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_matches, f, indent=4)
        print("Database updated with new entries.")

if __name__ == "__main__":
    scan_rescues()
