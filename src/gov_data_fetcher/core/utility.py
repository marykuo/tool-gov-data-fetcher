import os
import requests
import json


def fetch_api(url):
    response = requests.post(url)
    response.raise_for_status()  # Raise an error for bad status
    return response.json()


def save_json_to_file(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
