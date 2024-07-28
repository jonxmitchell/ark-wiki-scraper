import json
import time
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configurations
CREATURES_URL = 'https://ark.wiki.gg/wiki/Creature_IDs'
ITEMS_URL = 'https://ark.wiki.gg/wiki/Item_IDs'
ENGRAMS_URL = 'https://ark.wiki.gg/wiki/Engrams'
BLACKLIST_CONFIG = 'config.json'
BASE_URL = 'https://ark.wiki.gg'

def load_blacklist():
    with open(BLACKLIST_CONFIG, 'r') as f:
        config = json.load(f)
    return config.get('dino_blacklist', []), config.get('item_blacklist', []), config.get('engram_blacklist', [])

def init_webdriver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def click_element(driver, element):
    try:
        driver.execute_script("arguments[0].click();", element)
    except Exception as e:
        print(f"Error clicking element: {e}")

def format_title(title):
    return title.replace(' ', '_')

def get_creatures_list(url):
    print("Collecting creature data...")
    driver = init_webdriver(headless=True)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    show_buttons = driver.find_elements(By.CSS_SELECTOR, "span.jslink")
    for button in show_buttons:
        try:
            click_element(driver, button)
            time.sleep(1)
        except Exception as e:
            print(f"Error clicking 'show' button: {e}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    creatures = {}
    tables = soup.find_all('table', class_='wikitable')

    creature_id = 1

    for table in tables:
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue

            try:
                name_cell = cols[0].get_text(strip=True)
                entity_id = cols[3].get_text(strip=True)
                blueprint_cell = cols[4].get_text(strip=True)

                blueprint = blueprint_cell.split('\"')[1] if "\"" in blueprint_cell else "Unknown"

                name = name_cell.split(' (')[0]
                key_name = format_title(name)

                creatures[key_name] = {
                    "ID": creature_id,
                    "Type": "creature",
                    "Name": name,
                    "EntityID": entity_id,
                    "Blueprint": blueprint
                }

                print(f"Collected creature: {name} (ID: {creature_id})")
                creature_id += 1

            except Exception as e:
                print(f"Error processing row: {e}")

    return creatures

def get_items_list(url):
    print("Collecting item data...")
    driver = init_webdriver(headless=True)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    show_buttons = driver.find_elements(By.CSS_SELECTOR, "span.jslink")
    for button in show_buttons:
        try:
            click_element(driver, button)
            time.sleep(1)
        except Exception as e:
            print(f"Error clicking 'show' button: {e}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    items = {}
    tables = soup.find_all('table', class_='wikitable')

    item_id = 1

    for table in tables:
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            try:
                name_cell = cols[0].get_text(strip=True)
                class_name = cols[4].get_text(strip=True)
                blueprint_cell = cols[5].get_text(strip=True)

                blueprint = blueprint_cell.split('\"')[1] if "\"" in blueprint_cell else "Unknown"

                name = name_cell
                key_name = format_title(name)

                items[key_name] = {
                    "ID": item_id,
                    "Type": cols[1].get_text(strip=True),
                    "Name": name,
                    "ClassName": class_name,
                    "Blueprint": blueprint
                }

                print(f"Collected item: {name} (ID: {item_id})")
                item_id += 1

            except Exception as e:
                print(f"Error processing row: {e}")

    print(f"Total items collected: {len(items)}")
    return items

async def fetch_engram_details(session, url):
    try:
        async with session.get(url) as response:
            page_content = await response.text()
            soup = BeautifulSoup(page_content, 'html.parser')
            blueprint = "Unknown"
            name = "Unknown"

            name_tag = soup.select_one(".info-arkitex.info-X1-100.info-masthead")
            if name_tag:
                name = name_tag.get_text(strip=True)
                key_name = format_title(name)

            blueprint_tags = soup.select(".info-arkitex-spawn-commands-entry .copy-clipboard .copy-content")
            for tag in blueprint_tags:
                if 'Blueprint' in tag.get_text(strip=True):
                    blueprint = tag.get_text(strip=True).split('"')[1]
                    break

            return key_name, name, blueprint
    except Exception as e:
        print(f"Error fetching engram details from {url}: {e}")
        return "Unknown", "Unknown", "Unknown"

async def get_engrams_list(url):
    print("Collecting engram data...")
    driver = init_webdriver(headless=True)
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    engrams = {}
    tables = soup.find_all('table', class_='wikitable')

    engram_id = 1

    async with aiohttp.ClientSession() as session:
        tasks = []
        for table in tables:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 3:
                    continue

                try:
                    name_cell = cols[0].find('a')
                    if name_cell:
                        engram_page_url = BASE_URL + name_cell['href']
                        engram_type = "engram"

                        task = asyncio.ensure_future(fetch_engram_details(session, engram_page_url))
                        tasks.append((task, engram_id, engram_type))
                        engram_id += 1

                except Exception as e:
                    print(f"Error processing row: {e}")

        responses = await asyncio.gather(*[task[0] for task in tasks])

        for i, (task, engram_id, engram_type) in enumerate(tasks):
            key_name, name, blueprint = responses[i]
            if key_name != "Unknown":  # Only add engrams with valid names
                engrams[key_name] = {
                    "ID": engram_id,
                    "Type": engram_type,
                    "Name": name,
                    "Blueprint": blueprint
                }
                print(f"Collected engram: {name} (ID: {engram_id})")

    print(f"Total engrams collected: {len(engrams)}")
    return engrams

def main():
    creatures = get_creatures_list(CREATURES_URL)
    items = get_items_list(ITEMS_URL)
    engrams = asyncio.run(get_engrams_list(ENGRAMS_URL))
    
    dino_blacklist, item_blacklist, engram_blacklist = load_blacklist()
    
    filtered_creatures = {name: data for name, data in creatures.items() if not any(term in name for term in dino_blacklist)}
    filtered_items = {name: data for name, data in items.items() if not any(term in name for term in item_blacklist)}
    filtered_engrams = {name: data for name, data in engrams.items() if not any(term in name for term in engram_blacklist)}
    
    all_data = {
        "Dinos": filtered_creatures,
        "Items": filtered_items,
        "Engrams": filtered_engrams
    }

    print(f"Filtered Creatures: {len(filtered_creatures)}")
    print(f"Filtered Items: {len(filtered_items)}")
    print(f"Filtered Engrams: {len(filtered_engrams)}")

    with open('ark_data.json', 'w') as f:
        json.dump(all_data, f, indent=4)

    print("Data collection complete. Check 'ark_data.json' for results.")

if __name__ == "__main__":
    main()
