import requests
from bs4 import BeautifulSoup
import json
import re

BASE_URL = "https://ark.wiki.gg"
CREATURES_URL = f"{BASE_URL}/wiki/Creature_IDs"

def load_config(file_path='config.json'):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config.get('blacklist', [])

def is_blacklisted(name, blacklist):
    # Convert name to lower case for case-insensitive comparison
    name_lower = name.lower()
    # Check if any blacklisted term is present in the name
    for term in blacklist:
        if term.lower() in name_lower:
            print(f"Blacklist match found: {name} contains {term}")
            return True
    return False

def get_creatures_list(url, blacklist):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables on the page
    tables = soup.find_all('table', {'class': 'wikitable'})
    
    creatures = []
    for table in tables:
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 5:  # Ensure there are at least five cells
                name_cell = cells[0]
                entity_id_cell = cells[3]  # Entity ID is in the fourth cell
                blueprint_cell = cells[4]  # Blueprint Path is in the fifth cell
                
                # Extract name
                link = name_cell.find('a', title=True)
                creature_name = link['title'].strip() if link else "Unknown"
                
                # Extract Entity ID
                entity_id = entity_id_cell.get_text(strip=True)
                
                # Extract blueprint path
                blueprint_span = blueprint_cell.find('span', style="font-size:x-small;")
                if blueprint_span:
                    blueprint_text = blueprint_span.get_text(strip=True)
                    # Clean the blueprint path
                    blueprint_path = re.search(r'Blueprint\'[^\'"]*\'', blueprint_text)
                    blueprint_path = blueprint_path.group(0) if blueprint_path else blueprint_text.strip()
                else:
                    blueprint_path = "Unknown"
                
                # Check if the creature is blacklisted
                if not is_blacklisted(creature_name, blacklist):
                    creatures.append({
                        "ID": len(creatures) + 1,  # ID is a number starting from 1
                        "Type": "creature",
                        "Name": creature_name,
                        "EntityID": entity_id,
                        "Blueprint": blueprint_path
                    })
                else:
                    print(f"Skipping blacklisted creature: {creature_name}")
    
    return creatures

def main():
    blacklist = load_config()
    
    print(f"Blacklist loaded: {blacklist}")

    creatures = get_creatures_list(CREATURES_URL, blacklist)
    if not creatures:
        print("No creatures found.")
        return
    
    print(f"Found {len(creatures)} creatures.")
    
    creature_data = {}
    for creature in creatures:
        name_key = creature['Name'].replace(' ', '_')
        creature_data[name_key] = creature
    
    with open('creature_data.json', 'w') as f:
        json.dump(creature_data, f, indent=4)
    
    print("Data collection completed and saved to creature_data.json")

if __name__ == "__main__":
    main()
