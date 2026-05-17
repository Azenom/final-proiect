from services.add_employees import employee_exists

class Employee:
    def __init__(self, id, first_name, last_name, department):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.department = department

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def normalize(self):
        self.first_name = self.first_name.strip().title()
        self.last_name = self.last_name.strip().title()
        self.department = self.department.strip()

        if len(self.department) <= 2:
            self.department = self.department.upper()
        else:
            self.department = self.department.title()

    def validate(self):
        if not self.first_name.strip():
            return "❌ First name is required"
        if not self.last_name.strip():
            return "❌ Last name is required"
        if employee_exists(self.first_name,self.last_name,self.id):
            return "❌ Employee already exists"
        return None