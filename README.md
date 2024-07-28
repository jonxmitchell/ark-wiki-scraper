# Ark Wiki Scraper 🦖📜

A Python script to scrape data from the Ark Wiki, focusing on creature and item data. This script uses requests, BeautifulSoup, and Selenium to extract and organize data into a JSON file.

## Features 🚀

- Scrapes Creature Data: Collects creature IDs, names, entity IDs, and blueprints from Ark Wiki's creature pages.
- Scrapes Item Data: Collects item IDs, names, class names, and blueprints from Ark Wiki's item pages.
- Configurable Blacklists: Allows exclusion of specific creatures or items using blacklists.
- Automatic Driver Management: Uses webdriver-manager to handle ChromeDriver setup.

## Requirements 📋

- Python 3.7 or later
- Chrome browser
- Required Python packages (listed below)

## Installation 🔧

1. Clone the Repository:

```bash
git clone https://github.com/jonxmitchell/ark-wiki-scrapper.git
cd ark-wiki-scrapper
```

2. Install Required Packages:

```bash
pip install -r requirements.txt
```

## Configuration ⚙️

1. Edit blacklist.json:
   This file contains blacklists for creatures and items. Modify as needed to exclude specific entries.

```json
{
	"Creatures": ["ExampleCreature"],
	"Items": ["ExampleItem"],
	"Engrams": ["ExampleEngram"],
	"Beacons": ["ExampleBeacon"]
}
```

2. Adjust URLs (if necessary):

Ensure the URLs for creature and item data are correctly set in the script.

## Usage 🛠️

1. Run the Script:

```bash
python main.py
```

2. Output:

   - ark_data.json: This file will be created in the project directory and will contain the scraped data. The file is structured as follows:

```json
{
	"Dinos": {
		"Creature_Name": {
			"ID": 1,
			"Type": "creature",
			"Name": "CreatureName",
			"EntityID": "EntityID",
			"Blueprint": "BlueprintPath"
		}
	},
	"Items": {
		"Item_Name": {
			"ID": 1,
			"Type": "ItemType",
			"Name": "ItemName",
			"ClassName": "ClassName",
			"Blueprint": "BlueprintPath"
		}
	},
	"Engrams": {
		"Engram_Name": {
			"ID": 1,
			"Type": "engram",
			"Name": "EngramName",
			"Blueprint": "BlueprintPath"
		}
	},
	"Beacons": {
		"Beacon_Name": {
			"ID": 1,
			"Type": "beacon",
			"Name": "BeaconName",
			"ClassName": "ClassName"
		}
	}
}
```

## Troubleshooting 🛠️

- Driver Issues: If you encounter issues with ChromeDriver, ensure that your Chrome browser version matches the ChromeDriver version. The script uses webdriver-manager to handle this automatically.
- Dependencies: If you face import errors, make sure all required packages are installed and that you are using the correct Python interpreter.

## Contributing 🤝

Feel free to submit issues or pull requests. Contributions are welcome!

## Acknowledgments 🙌

[Ark Wiki](https://ark.wiki.gg) for the data.
