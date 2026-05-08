import sqlite3
import csv

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

def import_assets_from_csv(file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        required_columns = ["category","brand","serial_number","purchase_date"]

        if not reader.fieldnames:
            conn.close()
            raise Exception("❌ CSV file is empty")

        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            conn.close()
            raise Exception(f"❌ Missing columns: {', '.join(missing)}")

        for row in reader:
            if (not row["category"].strip() or not row["brand"].strip() or not row["serial_number"].strip()):
                print("❌ Skipped invalid asset row")
                continue
            try:
                cursor.execute("""
                    INSERT INTO assets (
                        category,
                        brand,
                        serial_number,
                        purchase_date
                    )
                    VALUES (?, ?, ?, ?)
                """, (row["category"],row["brand"],row["serial_number"],row["purchase_date"]))

            except sqlite3.IntegrityError:
                print(f"Skipped duplicate: "f"{row['serial_number']}")

    conn.commit()
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

def asset_has_active_assignment(asset_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM assignments
        WHERE asset_id = ?
        AND status = 'Active'
    """, (asset_id,))

    active = cursor.fetchone() is not None
    conn.close()
    return active

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
        # close active assignment
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

def serial_exists(serial_number, exclude_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if exclude_id:
        cursor.execute("""
            SELECT id
            FROM assets
            WHERE serial_number = ?
            AND id != ?
        """, (serial_number, exclude_id))

    else:
        cursor.execute("""
            SELECT id
            FROM assets
            WHERE serial_number = ?
        """, (serial_number,))

    exists = cursor.fetchone() is not None
    conn.close()
    return exists