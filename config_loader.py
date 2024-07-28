import json

CONFIG_FILE = 'config.json'

def load_blacklist():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    dino_blacklist = config.get('dino_blacklist', [])
    item_blacklist = config.get('item_blacklist', [])
    engram_blacklist = config.get('engram_blacklist', [])

    return dino_blacklist, item_blacklist, engram_blacklist
