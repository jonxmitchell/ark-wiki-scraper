import json
import time
import requests
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
BLACKLIST_CONFIG = 'config.json'

def load_blacklist():
    with open(BLACKLIST_CONFIG, 'r') as f:
        config = json.load(f)
    return config.get('dino_blacklist', []), config.get('item_blacklist', [])

def init_webdriver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # Run in headless mode (optional)
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

def get_creatures_list(url):
    print("Collecting creature data...")
    driver = init_webdriver(headless=True)  # Use headless mode by default
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Click "show" to reveal all tables
    show_buttons = driver.find_elements(By.CSS_SELECTOR, "span.jslink")
    for button in show_buttons:
        try:
            click_element(driver, button)
            time.sleep(1)  # Wait for the content to load
        except Exception as e:
            print(f"Error clicking 'show' button: {e}")

    # Now parse the content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    creatures = {}
    tables = soup.find_all('table', class_='wikitable')

    creature_id = 1  # Initialize ID counter

    for table in tables:
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue

            try:
                name_cell = cols[0].get_text(strip=True)
                entity_id = cols[3].get_text(strip=True)
                blueprint_cell = cols[4].get_text(strip=True)

                # Clean up blueprint
                blueprint = blueprint_cell.split('\"')[1] if "\"" in blueprint_cell else "Unknown"

                # Extracting the name
                name = name_cell.split(' (')[0]

                # Assign incremental ID if not present
                creatures[name] = {
                    "ID": creature_id,
                    "Type": "creature",
                    "Name": name,
                    "EntityID": entity_id,
                    "Blueprint": blueprint
                }

                print(f"Collected creature: {name} (ID: {creature_id})")
                creature_id += 1  # Increment ID for next entry

            except Exception as e:
                print(f"Error processing row: {e}")

    return creatures

def get_items_list(url):
    print("Collecting item data...")
    driver = init_webdriver(headless=True)  # Use headless mode by default
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    # Click "show" to reveal all tables
    show_buttons = driver.find_elements(By.CSS_SELECTOR, "span.jslink")
    for button in show_buttons:
        try:
            click_element(driver, button)
            time.sleep(1)  # Wait for the content to load
        except Exception as e:
            print(f"Error clicking 'show' button: {e}")

    # Now parse the content
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    items = {}
    tables = soup.find_all('table', class_='wikitable')

    item_id = 1  # Initialize ID counter

    for table in tables:
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue

            try:
                name_cell = cols[0].get_text(strip=True)
                class_name = cols[4].get_text(strip=True)
                blueprint_cell = cols[5].get_text(strip=True)

                # Clean up blueprint
                blueprint = blueprint_cell.split('\"')[1] if "\"" in blueprint_cell else "Unknown"

                # Extracting the name
                name = name_cell

                # Assign incremental ID if not present
                items[name] = {
                    "ID": item_id,
                    "Type": cols[1].get_text(strip=True),
                    "Name": name,
                    "ClassName": class_name,
                    "Blueprint": blueprint
                }

                print(f"Collected item: {name} (ID: {item_id})")
                item_id += 1  # Increment ID for next entry

            except Exception as e:
                print(f"Error processing row: {e}")

    return items

def main():
    creatures = get_creatures_list(CREATURES_URL)
    items = get_items_list(ITEMS_URL)
    
    # Load the blacklist
    dino_blacklist, item_blacklist = load_blacklist()
    
    # Filter out blacklisted items
    filtered_creatures = {name: data for name, data in creatures.items() if not any(term in name for term in dino_blacklist)}
    filtered_items = {name: data for name, data in items.items() if not any(term in name for term in item_blacklist)}
    
    # Combine data
    all_data = {
        "Dinos": filtered_creatures,
        "Items": filtered_items
    }

    # Write data to JSON file
    with open('ark_data.json', 'w') as f:
        json.dump(all_data, f, indent=4)

    print("Data collection complete. Check 'ark_data.json' for results.")

if __name__ == "__main__":
    main()
