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

BASE_URL = 'https://ark.wiki.gg'

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

def get_creatures_list():
    print("Collecting creature data...")
    driver = init_webdriver(headless=True)
    driver.get(BASE_URL + '/wiki/Creature_IDs')
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

def get_items_list():
    print("Collecting item data...")
    driver = init_webdriver(headless=True)
    driver.get(BASE_URL + '/wiki/Item_IDs')
    wait = WebDriverWait(driver, 10)

    show_buttons = driver.find_elements(By.CSS_SELECTOR, "span.jslink")
    
    for button in show_buttons:
        retries = 3
        for _ in range(retries):
            try:
                click_element(driver, button)
                time.sleep(1)
                if "hidden" not in button.get_attribute("class"):
                    break
            except Exception as e:
                print(f"Error clicking 'show' button: {e}")
                time.sleep(1)

    # Wait for all dynamic content to be fully loaded
    time.sleep(5)

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
                    "Type": cols[1].get_text(strip=True) or "Unknown",
                    "Name": name,
                    "ClassName": class_name or "Unknown",
                    "Blueprint": blueprint
                }

                print(f"Collected item: {name} (ID: {item_id})")
                item_id += 1

            except Exception as e:
                print(f"Error processing row: {e}")

    print(f"Total items collected: {len(items)}")
    return items

async def get_engrams_list():
    print("Collecting engram data...")
    driver = init_webdriver(headless=True)
    driver.get(BASE_URL + '/wiki/Engrams')
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

async def fetch_engram_details(session, engram_page_url):
    try:
        async with session.get(engram_page_url) as response:
            page_content = await response.text()
            soup = BeautifulSoup(page_content, 'html.parser')

            name_element = soup.find('div', class_='info-arkitex info-X1-100 info-masthead')
            name = name_element.get_text(strip=True) if name_element else "Unknown"
            key_name = name.replace(' ', '_')

            blueprint = "Unknown"
            blueprint_elements = soup.find_all('div', class_='info-arkitex-spawn-commands-entry')

            for element in blueprint_elements:
                code_elements = element.find_all('code', class_='copy-clipboard')
                for code in code_elements:
                    if 'giveitem' in code.get_text(strip=True):
                        blueprint = code.get_text(strip=True).split('"')[1]
                        break
                if blueprint != "Unknown":
                    break

            return key_name, name, blueprint

    except Exception as e:
        print(f"Error fetching engram details from {engram_page_url}: {e}")
        return "Unknown", "Unknown", "Unknown"
