import yaml
import os

def init_config():
    config_file = os.path.dirname(__file__) + '/config.yml'
    with open(config_file, 'r') as f:
        config = yaml.load(f)

    return config
