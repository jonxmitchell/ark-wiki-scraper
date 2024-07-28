import json

def load_blacklist():
    try:
        with open('blacklist.json', 'r') as f:
            blacklist = json.load(f)
            dino_blacklist = blacklist.get("Creatures", [])
            item_blacklist = blacklist.get("Items", [])
            engram_blacklist = blacklist.get("Engrams", [])
            beacon_blacklist = blacklist.get("Beacons", [])
    except FileNotFoundError:
        dino_blacklist = []
        item_blacklist = []
        engram_blacklist = []
        beacon_blacklist = []

    return dino_blacklist, item_blacklist, engram_blacklist, beacon_blacklist
