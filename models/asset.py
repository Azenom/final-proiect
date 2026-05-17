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

    def normalize(self):
        self.category = self.category.strip().title()
        cleaned_brand = self.brand.strip()

        if len(cleaned_brand) <= 2:
            self.brand = cleaned_brand.upper()
        else:
            self.brand = cleaned_brand.title()
        self.serial_number = self.serial_number.strip().upper()

    def validate(self):
        if not self.category.strip():
            return "❌ Category is required"
        if not self.brand.strip():
            return "❌ Brand is required"
        if not self.serial_number.strip():
            return "❌ Serial number is required"

        allowed_statuses = ["Available","Assigned","Service"]
        if self.status not in allowed_statuses:
            return "❌ Invalid asset status"
        
        if self.purchase_date:
            purchase = date.fromisoformat(self.purchase_date)
            if purchase > date.today():
                return "❌ Purchase date cannot be in the future"

        return None