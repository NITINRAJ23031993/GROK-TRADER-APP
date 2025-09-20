import yaml
import os

def load_config(path='config/settings.yaml'):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, 'r') as f:
        return yaml.safe_load(f)