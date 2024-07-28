import json
import asyncio
from data_fetchers import get_creatures_list, get_items_list, get_engrams_list, get_beacons_list
from config import load_blacklist

BASE_URL = 'https://ark.wiki.gg'

def main():
    creatures_url = BASE_URL + '/wiki/Creature_IDs'
    items_url = BASE_URL + '/wiki/Item_IDs'
    engrams_url = BASE_URL + '/wiki/Engrams'
    beacons_url = BASE_URL + '/wiki/Beacon_IDs'

    dino_blacklist, item_blacklist, engram_blacklist, beacon_blacklist = load_blacklist()

    creatures = get_creatures_list(creatures_url)
    items = get_items_list(items_url)
    engrams = asyncio.run(get_engrams_list(engrams_url))
    beacons = get_beacons_list(beacons_url)

    filtered_creatures = {k: v for k, v in creatures.items() if k not in dino_blacklist}
    filtered_items = {k: v for k, v in items.items() if k not in item_blacklist}
    filtered_engrams = {k: v for k, v in engrams.items() if k not in engram_blacklist}
    filtered_beacons = {k: v for k, v in beacons.items() if k not in beacon_blacklist}

    data = {
        "Creatures": filtered_creatures,
        "Items": filtered_items,
        "Engrams": filtered_engrams,
        "Beacons": filtered_beacons,
    }

    with open('ark_data.json', 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Total creatures: {len(filtered_creatures)}")
    print(f"Total items: {len(filtered_items)}")
    print(f"Total engrams: {len(filtered_engrams)}")
    print(f"Total beacons: {len(filtered_beacons)}")

if __name__ == '__main__':
    main()
