from models.asset import Asset
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
        """, (category,brand,serial_number,purchase_date))
        conn.commit()
        return None

    except sqlite3.IntegrityError:
        return "❌ Serial number already exists"

def import_assets_from_csv(file_path):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    imported = 0
    duplicates = 0
    invalid = 0

    with open(file_path,newline='',encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        required_columns = ["category","brand","serial_number","purchase_date"]

        if not reader.fieldnames:
            conn.close()
            raise Exception("❌ CSV file is empty")
        
        missing = [col for col in required_columns if col not in reader.fieldnames]
        if missing:
            conn.close()
            raise Exception(
                f"❌ Missing columns: "
                f"{', '.join(missing)}" )

        for row in reader:
            if ( not row["category"].strip() or not row["brand"].strip() or not row["serial_number"].strip() ):
                invalid += 1
                continue
            try:
                asset = Asset(None,row["category"],row["brand"],row["serial_number"],"Available",row["purchase_date"])
                asset.normalize()

                cursor.execute("""
                    INSERT INTO assets (
                        category,
                        brand,
                        serial_number,
                        purchase_date
                    )
                    VALUES (?, ?, ?, ?)
                """, (asset.category,asset.brand,asset.serial_number,row["purchase_date"]))
                imported += 1
            except sqlite3.IntegrityError:
                duplicates += 1

    conn.commit()
    conn.close()
    return {"imported": imported,"duplicates": duplicates,"invalid": invalid}

def get_all_assets(sort_by="status"):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    allowed_sorts = {"status": "status","category": "category","brand": "brand"}
    sort_column = allowed_sorts.get(sort_by, "status")
    query = f"""
        SELECT *
        FROM assets
        ORDER BY {sort_column}"""
    cursor.execute(query)

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