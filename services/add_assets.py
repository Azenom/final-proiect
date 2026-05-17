from models.asset import Asset
import sqlite3
import csv

DB_PATH = "data/inventory.db"


def add_asset(category, brand, serial_number, purchase_date):

    if serial_exists(serial_number):
        return "❌ Serial number already exists"

    try:
        with sqlite3.connect(DB_PATH) as conn:

            conn.execute("PRAGMA foreign_keys = ON")

            conn.execute("""
                INSERT INTO assets (
                    category,
                    brand,
                    serial_number,
                    purchase_date
                )
                VALUES (?, ?, ?, ?)
            """, (
                category,
                brand,
                serial_number,
                purchase_date
            ))

        return None

    except sqlite3.IntegrityError:
        return "❌ Serial number already exists"


def import_assets_from_csv(file_path):

    imported = 0
    duplicates = 0
    invalid = 0

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        with open(file_path, newline='', encoding='utf-8') as csvfile:

            reader = csv.DictReader(csvfile)

            required_columns = [
                "category",
                "brand",
                "serial_number",
                "purchase_date"
            ]

            if not reader.fieldnames:
                return "❌ CSV file is empty"

            reader.fieldnames = [
                field.strip().lower()
                for field in reader.fieldnames
            ]

            missing = [
                col
                for col in required_columns
                if col not in reader.fieldnames
            ]

            if missing:
                return (
                    "❌ Invalid CSV header. "
                    "Required columns: "
                    "category, brand, serial_number, purchase_date"
                )

            for row in reader:

                row = {
                    k.strip().lower(): v
                    for k, v in row.items()
                }

                if (
                    not row["category"].strip()
                    or not row["brand"].strip()
                    or not row["serial_number"].strip()
                ):
                    invalid += 1
                    continue

                try:

                    asset = Asset(
                        None,
                        row["category"],
                        row["brand"],
                        row["serial_number"],
                        "Available",
                        row["purchase_date"]
                    )

                    asset.normalize()

                    error = asset.validate()

                    if error:
                        invalid += 1
                        continue

                    cursor.execute("""
                        INSERT INTO assets (
                            category,
                            brand,
                            serial_number,
                            purchase_date
                        )
                        VALUES (?, ?, ?, ?)
                    """, (
                        asset.category,
                        asset.brand,
                        asset.serial_number,
                        asset.purchase_date
                    ))

                    imported += 1

                except sqlite3.IntegrityError:
                    duplicates += 1

    return {
        "imported": imported,
        "duplicates": duplicates,
        "invalid": invalid
    }


def get_all_assets(sort_by="status"):

    allowed_sorts = {
        "status": "status",
        "category": "category",
        "brand": "brand"
    }

    sort_column = allowed_sorts.get(sort_by, "status")

    query = f"""
        SELECT *
        FROM assets
        ORDER BY {sort_column}
    """

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(query)

        return cursor.fetchall()


def get_asset_by_id(asset_id):

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM assets
            WHERE id = ?
        """, (asset_id,))

        return cursor.fetchone()


def asset_has_active_assignment(asset_id):

    with sqlite3.connect(DB_PATH) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM assignments
            WHERE asset_id = ?
            AND status = 'Active'
        """, (asset_id,))

        return cursor.fetchone() is not None


def delete_asset(asset_id):

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM assignments
            WHERE asset_id = ?
        """, (asset_id,))

        cursor.execute("""
            DELETE FROM assets
            WHERE id = ?
        """, (asset_id,))


def update_asset(asset_id, category, brand, serial, status):

    if serial_exists(serial, asset_id):
        return "❌ Serial number already exists"

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        if status == "Service":

            cursor.execute("""
                UPDATE assignments
                SET status = 'Returned',
                    returned_date = DATE('now')
                WHERE asset_id = ?
                AND status = 'Active'
            """, (asset_id,))

        cursor.execute("""
            UPDATE assets
            SET category = ?,
                brand = ?,
                serial_number = ?,
                status = ?
            WHERE id = ?
        """, (
            category,
            brand,
            serial,
            status,
            asset_id
        ))

    return None


def serial_exists(serial_number, exclude_id=None):

    serial_number = serial_number.strip().upper()

    with sqlite3.connect(DB_PATH) as conn:

        cursor = conn.cursor()

        if exclude_id:

            cursor.execute("""
                SELECT id
                FROM assets
                WHERE serial_number = ?
                AND id != ?
            """, (
                serial_number,
                exclude_id
            ))

        else:

            cursor.execute("""
                SELECT id
                FROM assets
                WHERE serial_number = ?
            """, (serial_number,))

        return cursor.fetchone() is not None