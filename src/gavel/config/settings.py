import os

TPTP_ROOT = os.environ.get("TPTP_ROOT", "")

DBMS = os.environ.get("GAVEL_DBMS", "sqlite")

DB_CONNECTION = dict(
    user=os.environ.get("GAVEL_DB_USER", ""),
    password=os.environ.get("GAVEL_DB_PASSWORD", ""),
    host=os.environ.get("GAVEL_DB_HOST", ""),
    port=os.environ.get("GABEL_DB_PORT", ""),
    database=os.environ.get("GAVEL_DB_NAME", ":memory:"),
)

HETS_HOST = os.environ.get("HETS_HOST", "localhost")
HETS_PORT = os.environ.get("HETS_PORT", 8000)
