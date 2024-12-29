import yaml
from munch import Munch
from pathlib import Path

def load():
    config_file = '/home/pmorch/.config/polyopen/config.yaml'
    config = yaml.safe_load(Path(config_file).read_bytes())
    config = Munch.fromDict(config)
    return config
    