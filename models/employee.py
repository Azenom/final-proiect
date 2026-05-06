class Employee:

    def __init__(self, id, first_name, last_name, department):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.department = department

    def full_name(self):
        return f"{self.first_name} {self.last_name}"