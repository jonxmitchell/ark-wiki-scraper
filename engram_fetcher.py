import aiohttp
from bs4 import BeautifulSoup

BASE_URL = 'https://ark.wiki.gg'

def format_title(title):
    return title.replace(' ', '_')

async def fetch_engram_details(session, url):
    try:
        async with session.get(url) as response:
            page_content = await response.text()
            soup = BeautifulSoup(page_content, 'html.parser')
            blueprint = "Unknown"
            name = "Unknown"
            
            name_tag = soup.find('div', class_='info-arkitex info-unit-row')
            if name_tag:
                name = name_tag.get_text(strip=True)
                key_name = format_title(name)
            else:
                key_name = "Unknown"

            blueprint_tag = soup.find('div', class_='info-arkitex-spawn-commands-entry')
            if blueprint_tag:
                blueprint_code = blueprint_tag.find_all('code')
                if len(blueprint_code) > 1:
                    blueprint = blueprint_code[1].get_text(strip=True)
                    blueprint = blueprint.split('\"')[1] if "\"" in blueprint else "Unknown"

            return key_name, name, blueprint
    except Exception as e:
        print(f"Error fetching engram details for {url}: {e}")
        return "Unknown", "Unknown", "Unknown"
