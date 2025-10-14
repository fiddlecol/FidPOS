# utils/backup.py
import sqlite3
import os

def backup_database(backup_file="backup.sql", db_path="fidpos.db"):
    """
    Create a SQL dump of the current SQLite database.
    """
    if not os.path.exists(db_path):
        print("⚠️ Database not found — skipping backup.")
        return

    try:
        conn = sqlite3.connect(db_path)
        with open(backup_file, "w", encoding="utf-8") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        conn.close()
        print(f"✅ Backup created: {backup_file}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")
