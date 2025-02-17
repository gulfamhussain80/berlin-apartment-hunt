from lxml import html as html
import requests
import json
import os
import time
import threading



def save_to_json(new_items, filename="berlin_aps.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    existing_set = {tuple(ap.items()) for ap in existing_data}
    unique_items = [item for item in new_items if tuple(item.items()) not in existing_set]

    if unique_items:
        
        for unique_item in unique_items:
            print(f"New Apartment listed: {unique_item['link']}")
        existing_data.extend(unique_items)
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)
        
        
        
        def play_beep():
            while not stop_event.is_set():
                os.system('afplay /System/Library/Sounds/Glass.aiff')

        stop_event = threading.Event()
        beep_thread = threading.Thread(target=play_beep, daemon=True)
        beep_thread.start()

        while True:
            user_input = input("New apartment listed! Press 'y' or Enter to stop the alert: ")
            if user_input.lower() == 'y' or user_input == '':
                stop_event.set()
                break




def scrape_website():
    url = "https://www.wbm.de/wohnungen-berlin/angebote/"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.6",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.wbm.de",
        "Referer": "https://www.wbm.de/wohnungen-berlin/angebote/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Sec-GPC": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Brave";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS"
    }
    data = {
        "tx_openimmo_immobilie[search]": "search",
        "tx_openimmo_immobilie[page]": "1",
        "tx_openimmo_immobilie[ort]": "Berlin",
        "tx_openimmo_immobilie[wohnflaeche]": "0_0",
        "tx_openimmo_immobilie[anzahlZimmer]": "0_0",
        "tx_openimmo_immobilie[warmmiete]": "0_0"
    }
    
    response = requests.post(url, headers=headers, data=data)
    print(response)
    if response.status_code == 200:
        tree = html.fromstring(response.text)
        found_aps=[]
        items = tree.xpath("//div[contains(@class, 'openimmo-search-list-item')]")
        for item in items:
            links = item.xpath(".//div[@class='btn-holder']/a/@href")
            item_link = links[0] if links else None
            item_id = item.get("data-id")
            item_uid = item.get("data-uid")
            
            found_aps.append({
                "id": item_id,
                "uid": item_uid,
                "link": f"https://www.wbm.de{item_link}"
            })
        
        return found_aps
    else:
        return []

def find_and_update_list():
    items = scrape_website()
    save_to_json(items)


while True:
    find_and_update_list()
    time.sleep(120)
