import os
from pathlib import Path

from dotenv import load_dotenv


# ==========================
# DIRECTORIO BASE DEL PROYECTO
# ==========================

BASE_DIR = Path(__file__).resolve().parents[1]

# Carga variables desde .env (si existe) al entorno del proceso.
# En Streamlit Community Cloud no hace falta: ahi las variables se
# configuran en "Advanced settings" > Secrets, no via .env.
load_dotenv(BASE_DIR / ".env")


# ==========================
# CONFIGURACION DESDE .env
# ==========================

APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# ==========================
# DATA (fuente cruda)
# ==========================

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"


# ==========================
# OUTPUT (artefactos generados por el ETL)
# ==========================

OUTPUT_DIR = BASE_DIR / "output"
PARQUET_PATH = OUTPUT_DIR / "ventas.parquet"
DB_PATH = OUTPUT_DIR / "ventas.duckdb"


# ==========================
# LOGS
# ==========================

LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "etl.log"


# ==========================
# CREACION DE CARPETAS
# ==========================

for _dir in (RAW_DIR, OUTPUT_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)
