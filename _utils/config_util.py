import os
import json


def get_config():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(script_dir, '../config.json')
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    return config


if __name__ == '__main__':
    get_config()
    