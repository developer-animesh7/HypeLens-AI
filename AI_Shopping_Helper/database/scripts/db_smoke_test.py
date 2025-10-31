import os, sys

# Ensure project root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database.db_connection import DatabaseConnection

def main():
    db = DatabaseConnection()
    db.connect()
    # Simple smoke test
    rows = db.execute_query("SELECT 1 as ok")
    print({"ok": rows[0]["ok"] if rows else None})

if __name__ == "__main__":
    main()
