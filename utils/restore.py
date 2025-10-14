# utils/restore.py
import sqlite3
import os

def restore_database(backup_file="backup.sql", db_path="fidpos.db"):
    """
    Restore the SQLite database from a backup SQL file.
    """
    if not os.path.exists(backup_file):
        print("⚠️ No backup file found — skipping restore.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        with open(backup_file, "r", encoding="utf-8") as f:
            sql = f.read()
            cursor.executescript(sql)

        conn.commit()
        conn.close()
        print("✅ Database restored successfully.")
    except Exception as e:
        print(f"❌ Restore failed: {e}")
