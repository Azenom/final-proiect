import sqlite3

DB_PATH = "data/inventory.db"

def add_asset(category, brand, serial_number, purchase_date):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO assets (
                category,
                brand,
                serial_number,
                purchase_date
            )
            VALUES (?, ?, ?, ?)
        """, (category, brand, serial_number, purchase_date))

        conn.commit()
        print("✅ Asset added successfully!")

    except sqlite3.IntegrityError as e:
        print("❌ Error:", e)

    finally:
        conn.close()