from pathlib import Path


# ==========================
# DIRECTORIO BASE DEL PROYECTO
# ==========================

BASE_DIR = Path(__file__).resolve().parents[2]


# ==========================
# DATA
# ==========================

DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"


# ==========================
# DATABASE
# ==========================

DATABASE_DIR = BASE_DIR / "database"

DB_PATH = DATABASE_DIR / "ventas.duckdb"



# ==========================
# CREACION DE CARPETAS
# ==========================

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)


DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)