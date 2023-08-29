import os
import yaml

config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')

# Load configuration from config.yaml
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)
