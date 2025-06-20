import requests
import json
import os

API_URL = 'https://pinout-api.onrender.com/list-submissions-files'
PINOUTS_FILE = 'pinouts.json'

def fetch_submissions():
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json()

def load_main_pinouts():
    if os.path.exists(PINOUTS_FILE):
        with open(PINOUTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return []

def save_main_pinouts(pinouts):
    with open(PINOUTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(pinouts, f, ensure_ascii=False, indent=2)

def main():
    submissions = fetch_submissions()
    main_pinouts = load_main_pinouts()
    # Only add new pinouts that are not already present
    existing = set(json.dumps(p, sort_keys=True) for p in main_pinouts)
    new_count = 0
    for sub in submissions:
        data = sub['data']
        if json.dumps(data, sort_keys=True) not in existing:
            main_pinouts.append(data)
            new_count += 1
    if new_count > 0:
        save_main_pinouts(main_pinouts)
        print(f"Added {new_count} new pinouts. Saved to {PINOUTS_FILE}.")
    else:
        print("No new pinouts added.")

if __name__ == '__main__':
    main()
