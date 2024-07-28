import json
import asyncio
from scraper import get_creatures_list, get_items_list, get_engrams_list
from utils import load_blacklist

def main():
    creatures = get_creatures_list()
    items = get_items_list()
    engrams = asyncio.run(get_engrams_list())
    
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
