from models.asset import Asset

from services.logger import logger

import sqlite3
import csv


DB_PATH: str = "data/inventory.db"


def add_asset(
    category: str,
    brand: str,
    serial_number: str,
    purchase_date: str | None
) -> str | None:
    """
    Add a new asset to the database.

    Returns:
        Error message or None.
    """

    if serial_exists(serial_number):

        logger.warning(
            f"Duplicate serial number detected: "
            f"{serial_number}"
        )

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

        logger.info(
            f"Asset inserted successfully: "
            f"{serial_number}"
        )

        return None

    except sqlite3.IntegrityError:

        logger.error(
            f"Asset insertion failed: "
            f"{serial_number}"
        )

        return "❌ Serial number already exists"


def import_assets_from_csv(
    file_path: str
) -> dict[str, int] | str:
    """
    Import assets from a CSV file.

    Returns:
        Import statistics or error message.
    """

    imported = 0
    duplicates = 0
    invalid = 0

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("PRAGMA foreign_keys = ON")

        cursor = conn.cursor()

        with open(
            file_path,
            newline='',
            encoding='utf-8'
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            required_columns = [
                "category",
                "brand",
                "serial_number",
                "purchase_date"
            ]

            if not reader.fieldnames:

                logger.warning(
                    "Asset CSV import failed: empty file"
                )

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

                logger.warning(
                    "Asset CSV import failed: "
                    "invalid headers"
                )

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

    logger.info(
        f"Assets CSV imported | "
        f"Imported: {imported} | "
        f"Duplicates: {duplicates} | "
        f"Invalid: {invalid}"
    )

    return {
        "imported": imported,
        "duplicates": duplicates,
        "invalid": invalid
    }


def get_all_assets(
    sort_by: str = "status"
) -> list[sqlite3.Row]:
    """
    Retrieve all assets sorted by the selected column.
    """

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


def get_asset_by_id(
    asset_id: int
) -> sqlite3.Row | None:
    """
    Retrieve an asset by ID.
    """

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM assets
            WHERE id = ?
        """, (asset_id,))

        return cursor.fetchone()


def asset_has_active_assignment(
    asset_id: int
) -> bool:
    """
    Check whether an asset has an active assignment.
    """

    with sqlite3.connect(DB_PATH) as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM assignments
            WHERE asset_id = ?
            AND status = 'Active'
        """, (asset_id,))

        return cursor.fetchone() is not None


def delete_asset(asset_id: int) -> None:
    """
    Delete an asset and its assignments.
    """

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

    logger.info(
        f"Asset deleted successfully: "
        f"{asset_id}"
    )


def update_asset(
    asset_id: int,
    category: str,
    brand: str,
    serial: str,
    status: str
) -> str | None:
    """
    Update asset information.

    Returns:
        Error message or None.
    """

    if serial_exists(serial, asset_id):

        logger.warning(
            f"Asset update failed due to duplicate "
            f"serial number: {serial}"
        )

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

    logger.info(
        f"Asset updated successfully: "
        f"{asset_id}"
    )

    return None


def serial_exists(
    serial_number: str,
    exclude_id: int | None = None
) -> bool:
    """
    Check whether a serial number already exists.
    """

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