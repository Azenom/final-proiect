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

def get_all_assets():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM assets")

    data = cursor.fetchall()
    conn.close()
    return data

def get_asset_by_id(asset_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM assets WHERE id = ?
    """, (asset_id,))
    asset = cursor.fetchone()
    conn.close()
    return asset

def delete_asset(asset_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assignments WHERE asset_id = ?", (asset_id,))
    cursor.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()

def update_asset(asset_id, category, brand, serial, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if status == "Service":
        cursor.execute("""
            UPDATE assignments
            SET status='Returned', returned_date=DATE('now')
            WHERE asset_id=? AND status='Active'
        """, (asset_id,))

    cursor.execute("""
        UPDATE assets
        SET category=?, brand=?, serial_number=?, status=?
        WHERE id=?
    """, (category, brand, serial, status, asset_id))

    conn.commit()
    conn.close()