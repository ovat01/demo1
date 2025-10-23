import configparser
import os

CONFIG_FILE = 'config.ini'

def save_config(folder_path, printer_name):
    """Saves the configuration to the config file."""
    config = configparser.ConfigParser()
    config['Settings'] = {
        'folder_path': folder_path,
        'printer_name': printer_name
    }

    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    except IOError as e:
        print(f"Error al guardar la configuración: {e}")

def load_config():
    """Loads the configuration from the config file."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        return None, None

    try:
        config.read(CONFIG_FILE)
        folder_path = config.get('Settings', 'folder_path', fallback=None)
        printer_name = config.get('Settings', 'printer_name', fallback=None)
        return folder_path, printer_name
    except (configparser.Error, IOError) as e:
        print(f"Error al cargar la configuración: {e}")
        return None, None
