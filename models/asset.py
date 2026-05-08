from services.add_assets import serial_exists
from datetime import date

class Asset:

    def __init__(self, id, category, brand, serial_number, status, purchase_date=None):
        self.id = id
        self.category = category
        self.brand = brand
        self.serial_number = serial_number
        self.status = status
        self.purchase_date = purchase_date

    def full_name(self):
        return f"{self.category} - {self.brand}"

    def serial(self):
        return f"SN: {self.serial_number}"

    def is_available(self):
        return self.status == "Available"

    def validate(self):

        if not self.category.strip():
            return "❌ Category is required"

        if not self.brand.strip():
            return "❌ Brand is required"

        if not self.serial_number.strip():
            return "❌ Serial number is required"

        if serial_exists(self.serial_number, self.id):
            return "❌ Serial number already exists"

        allowed_statuses = ["Available","Assigned","Service"]

        if self.status not in allowed_statuses:
            return "❌ Invalid asset status"
        
        if self.purchase_date:
            purchase = date.fromisoformat(self.purchase_date)
            if purchase > date.today():
                return "❌ Purchase date cannot be in the future"

        return None