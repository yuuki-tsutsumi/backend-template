import json
import os
from logging import Logger, config, getLogger


def setup_logger(name: str) -> Logger:
    logs_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    log_file_path = "/log_config.json"

    with open(os.getcwd() + log_file_path, "r") as f:
        log_conf = json.load(f)

    config.dictConfig(log_conf)

    return getLogger(name)
