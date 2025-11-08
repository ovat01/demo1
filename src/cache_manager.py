import json
import os
from datetime import datetime

CACHE_FILE_NAME = ".boletas_cache.json"

def get_cache_path(folder_path):
    """Returns the full path to the cache file for a given folder."""
    return os.path.join(folder_path, CACHE_FILE_NAME)

def load_cache(folder_path):
    """
    Loads the cache data from the JSON file in the specified folder.
    Returns an empty dictionary if the cache file doesn't exist or is invalid.
    """
    cache_path = get_cache_path(folder_path)
    if not os.path.exists(cache_path):
        return {}
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If the file is corrupted or unreadable, start with a fresh cache
        return {}

def save_cache(folder_path, cache_data):
    """
    Saves the cache data to the JSON file in the specified folder.
    """
    cache_path = get_cache_path(folder_path)
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=4)
    except IOError as e:
        print(f"Error saving cache file: {e}")

def is_file_modified(file_path, cached_mtime_str):
    """
    Checks if a file's modification time is different from the cached time.
    """
    try:
        # Get current modification time as a timestamp
        current_mtime = os.path.getmtime(file_path)
        # The cached time is already a string representation of the timestamp
        return str(current_mtime) != cached_mtime_str
    except OSError:
        # If the file is deleted or inaccessible, treat it as modified
        return True
