import yaml
import os
import sys


def load_config(path_to_config="./configs/config.json") -> dict:
    try:
        with open(path_to_config, "r") as fh:
            config = yaml.load(fh, Loader=yaml.FullLoader)
    except OSError:
        print("CRITICAL error while opening configuration file!")
        sys.exit(1)

    return config
