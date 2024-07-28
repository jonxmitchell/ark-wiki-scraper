import json

BLACKLIST_CONFIG = 'config.json'

def load_blacklist():
    with open(BLACKLIST_CONFIG, 'r') as f:
        config = json.load(f)
    return config.get('dino_blacklist', []), config.get('item_blacklist', []), config.get('engram_blacklist', [])
