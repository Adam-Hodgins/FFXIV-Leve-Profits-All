import os
import json
import time
import requests

# === Configuration ===
WORLDS = ffxiv_servers = [
    # North America
    "Adamantoise", "Cactuar", "Faerie", "Gilgamesh", "Jenova",
    "Midgardsormr", "Sargatanas", "Siren",
    "Balmung", "Brynhildr", "Coeurl", "Diabolos", "Goblin",
    "Malboro", "Mateus", "Zalera",
    "Behemoth", "Excalibur", "Exodus", "Famfrit", "Hyperion",
    "Lamia", "Leviathan", "Ultros",
    "Halicarnassus", "Maduin", "Marilith", "Seraph", "Cuchulainn",
    "Golem", "Kraken", "Rafflesia",
    # Europe
    "Cerberus", "Louisoix", "Moogle", "Omega", "Phantom",
    "Ragnarok", "Sagittarius", "Spriggan",
    "Alpha", "Lich", "Odin", "Phoenix", "Raiden",
    "Shiva", "Twintania", "Zodiark",
    "Innocence", "Pixie", "Titania", "Tycoon",
    # Japan
    "Aegis", "Atomos", "Carbuncle", "Garuda", "Gungnir",
    "Kujata", "Tonberry", "Typhon",
    "Alexander", "Bahamut", "Durandal", "Fenrir", "Ifrit",
    "Ridill", "Tiamat", "Ultima",
    "Anima", "Asura", "Chocobo", "Hades", "Ixion",
    "Masamune", "Pandaemonium", "Titan",
    "Belias", "Mandragora", "Ramuh", "Shinryu", "Unicorn",
    "Valefor", "Yojimbo", "Zeromus",
    # Oceania
    "Bismarck", "Ravana", "Sephirot", "Sophia", "Zurvan"
]


INPUT_DIR       = 'Prepped Leves'
OUTPUT_BASE_DIR = 'Worlds'

API_URL = (
    'https://universalis.app/api/v2/{world}/{item_ids}'
    '?listings=0&entries=0'
    '&fields=items.currentAveragePrice%2Citems.currentAveragePriceNQ%2Citems.currentAveragePriceHQ'
)

BATCH_SIZE     = 100      # up to 100 IDs per request
REQUEST_DELAY  = 0.05     # seconds pause after each HTTP call
REQUEST_TIMEOUT = 10      # seconds

def fetch_prices_batch(item_ids, session, world):
    """
    Fetch prices for a list of item_ids on a specific world,
    return a dict mapping each item_id to its price dict.
    """
    ids_csv = ','.join(str(i) for i in item_ids)
    url = API_URL.format(world=world, item_ids=ids_csv)
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json().get('items', {})
    time.sleep(REQUEST_DELAY)
    # keys come back as strings
    return {int(k): v for k, v in data.items()}

def process_file_for_world(src_path, dst_path, session, world):
    fname = os.path.basename(src_path)
    try:
        with open(src_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[{world}/{fname}] Failed to load: {e}")
        return

    if not isinstance(data, list):
        print(f"[{world}/{fname}] Skipping (root is not a list)")
        return

    # Remove any old price fields
    for entry in data:
        entry.pop('currentAveragePrice',   None)
        entry.pop('currentAveragePriceNQ', None)
        entry.pop('currentAveragePriceHQ', None)

    # Build a map from Leve Item ID → list of entries
    id_to_entries = {}
    for entry in data:
        iid = entry.get('Leve Item ID')
        if isinstance(iid, int):
            id_to_entries.setdefault(iid, []).append(entry)

    if not id_to_entries:
        print(f"[{world}/{fname}] No valid Leve Item IDs found")
        return

    all_ids = list(id_to_entries.keys())
    batches = [
        all_ids[i : i + BATCH_SIZE]
        for i in range(0, len(all_ids), BATCH_SIZE)
    ]

    updated = False
    for batch in batches:
        try:
            prices_map = fetch_prices_batch(batch, session, world)
            for iid, price_info in prices_map.items():
                for entry in id_to_entries.get(iid, []):
                    entry['currentAveragePrice']   = price_info.get('currentAveragePrice')
                    entry['currentAveragePriceNQ'] = price_info.get('currentAveragePriceNQ')
                    entry['currentAveragePriceHQ'] = price_info.get('currentAveragePriceHQ')
            print(f"[{world}/{fname}] Updated batch {batch}")
            updated = True
        except Exception as e:
            print(f"[{world}/{fname}] Error fetching batch {batch}: {e}")

    # Write the updated file only if we fetched something
    if updated:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        try:
            with open(dst_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[{world}/{fname}] Written to {dst_path}")
        except Exception as e:
            print(f"[{world}/{fname}] Failed to write: {e}")

def main():
    if not os.path.isdir(INPUT_DIR):
        print(f"Input directory not found: {INPUT_DIR}")
        return

    with requests.Session() as session:
        for world in WORLDS:
            for fname in os.listdir(INPUT_DIR):
                if not fname.lower().endswith('.json'):
                    continue
                src = os.path.join(INPUT_DIR, fname)
                dst_dir = os.path.join(OUTPUT_BASE_DIR, world)
                dst = os.path.join(dst_dir, fname)
                process_file_for_world(src, dst, session, world)

if __name__ == '__main__':
    main()
