import requests
from bs4 import BeautifulSoup
import json
import re

BASE_URL = "https://ark.wiki.gg"
CREATURES_URL = f"{BASE_URL}/wiki/Creatures"

def get_creatures_list(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with creatures
    creature_table = soup.find('table', {'class': 'wikitable'})
    
    if not creature_table:
        print("Creature table not found.")
        return []

    creatures = []
    for row in creature_table.find_all('tr')[1:]:
        name_cell = row.find('td')
        if name_cell:
            link = name_cell.find('a', title=True)
            if link:
                creature_name = link['title'].strip()
                creature_url = BASE_URL + link['href']
                creatures.append((creature_name, creature_url))
    
    return creatures

def clean_variant_name(variant_name):
    return variant_name.replace("Variant ", "").strip()

def clean_blueprint(blueprint_text):
    # Extract the part of the blueprint path within the quotes
    match = re.search(r'Blueprint\'[^\'"]*\'', blueprint_text)
    return match.group(0) if match else blueprint_text.strip()

def get_creature_blueprints(creature_name, creature_url):
    response = requests.get(creature_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    spawn_command_divs = soup.find_all('div', {'class': 'info-arkitex-spawn-commands-entry'})
    
    blueprints = []
    for div in spawn_command_divs:
        variant_name_tag = div.find('p', {'style': 'font-size:1.1em;font-weight:bold;'})
        variant_name = variant_name_tag.text.strip() if variant_name_tag else creature_name
        variant_name = clean_variant_name(variant_name)  # Clean the variant name
        
        blueprint_code = div.find_all('code', {'class': 'copy-clipboard'})
        
        if blueprint_code and len(blueprint_code) > 1:
            blueprint_text = blueprint_code[1].find('span', {'class': 'copy-content'}).text.strip()
            cleaned_blueprint = clean_blueprint(blueprint_text)  # Clean the blueprint path
            blueprints.append((variant_name, cleaned_blueprint))
    
    return blueprints

def main():
    creatures = get_creatures_list(CREATURES_URL)
    if not creatures:
        print("No creatures found.")
        return
    
    print(f"Found {len(creatures)} creatures.")
    
    creature_data = {}
    for idx, (name, url) in enumerate(creatures, start=1):
        print(f"Processing creature: {name} ({url})")
        blueprints = get_creature_blueprints(name, url)
        
        if not blueprints:
            print(f"No blueprints found for {name}.")
        
        for variant_idx, (variant_name, blueprint) in enumerate(blueprints, start=1):
            print(f"  Found blueprint for variant: {variant_name}")
            print(f"    Blueprint: {blueprint}")
            creature_data[f"{variant_name.replace(' ', '_')}"] = {
                "ID": f"{idx}_{variant_idx}",
                "Name": variant_name,
                "Blueprint": blueprint,
                "Type": "creature"  # Added type field
            }
    
    with open('creature_data.json', 'w') as f:
        json.dump(creature_data, f, indent=4)
    
    print("Data collection completed and saved to creature_data.json")

if __name__ == "__main__":
    main()
