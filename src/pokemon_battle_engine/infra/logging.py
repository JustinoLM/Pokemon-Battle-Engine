# src/pokemon_battle_engine/infra/pokeapi_client.py

import logging
import sys
import structlog
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # 1. --- Configure JSONs Format ---
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()

        ],
        context_class= dict,
        logger_factory= structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 2. --- Configure logger at the Python Root ---
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # 3. --- Configure files Rotation ---
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # -- File handler to write in files --
    file_handler = RotatingFileHandler(
        f"{log_dir}/battle.log", maxBytes=10*1024*1024, backupCount=3
    )
    file_handler.setLevel(logging.INFO)

    # 4. --- Console Handler for the terminal ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

def get_logger():
    return structlog.get_logger()
