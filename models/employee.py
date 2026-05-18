class Employee:
    """
    Employee model used for employee management operations.
    """

    def __init__(
        self,
        id: int | None,
        first_name: str,
        last_name: str,
        department: str
    ) -> None:

        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.department = department

    def full_name(self) -> str:
        """
        Return employee full name.
        """

        return f"{self.first_name} {self.last_name}"

    def normalize(self) -> None:
        """
        Normalize employee data formatting to be without space and first letter upper 
        and/or both letters upper if there are only 2 or 1.
        """

        self.first_name = (
            self.first_name
            .strip()
            .title()
        )

        self.last_name = (
            self.last_name
            .strip()
            .title()
        )

        self.department = (
            self.department
            .strip()
        )

        if len(self.department) <= 2:
            self.department = self.department.upper()
        else:
            self.department = self.department.title()

    def validate(self) -> str | None:
        """
        Validate employee data.

        Returns:
            Validation error message or None.
        """

        if not self.first_name.strip():
            return "❌ First name is required"

        if not self.last_name.strip():
            return "❌ Last name is required"

        return None