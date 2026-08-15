"""
utils/logging_utils.py

Configuración centralizada de logging para todo el pipeline ETL.
Escribe tanto en consola como en logs/etl.log.
"""

import logging

from config.config import LOG_FILE, LOG_LEVEL


def configurar_logging():
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
        force=True,
    )
