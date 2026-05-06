class Asset:

    def __init__(self, id, category, brand, serial_number, status):
        self.id = id
        self.category = category
        self.brand = brand
        self.serial_number = serial_number
        self.status = status

    def full_name(self):
        return f"{self.category} - {self.brand}"

    def serial(self):
        return f"SN: {self.serial_number}"

    def is_available(self):
        return self.status == "Available"