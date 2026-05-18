from datetime import date

class Asset:
    """
    Asset model used for asset management operations.
    """

    def __init__(
        self,
        id: int | None,
        category: str,
        brand: str,
        serial_number: str,
        status: str,
        purchase_date: str | None = None
    ) -> None:

        self.id = id
        self.category = category
        self.brand = brand
        self.serial_number = serial_number
        self.status = status
        self.purchase_date = purchase_date

    def full_name(self) -> str:
        """
        Return formatted asset name.
        """

        return f"{self.category} - {self.brand}"

    def serial(self) -> str:
        """
        Return formatted serial number.
        """

        return f"SN: {self.serial_number}"

    def is_available(self) -> bool:
        """
        Check whether the asset is available.
        """

        return self.status == "Available"

    def normalize(self) -> None:
        """
        Normalize asset data formatting.
        """

        self.category = self.category.strip().title()

        cleaned_brand = self.brand.strip()

        if len(cleaned_brand) <= 2:
            self.brand = cleaned_brand.upper()
        else:
            self.brand = cleaned_brand.title()

        self.serial_number = (
            self.serial_number
            .strip()
            .upper()
        )

        if self.purchase_date:
            self.purchase_date = (
                self.purchase_date
                .strip()
            )

    def validate(self) -> str | None:
        """
        Validate asset data.

        Returns:
            Validation error message or None.
        """

        if not self.category.strip():
            return "❌ Category is required"

        if not self.brand.strip():
            return "❌ Brand is required"

        if not self.serial_number.strip():
            return "❌ Serial number is required"

        allowed_statuses = [
            "Available",
            "Assigned",
            "Service"
        ]

        if self.status not in allowed_statuses:
            return "❌ Invalid asset status"

        if self.purchase_date:

            try:
                purchase = date.fromisoformat(
                    self.purchase_date
                )

            except ValueError:
                return (
                    "❌ Invalid purchase date format "
                    "(YYYY-MM-DD required)"
                )

            if purchase > date.today():
                return (
                    "❌ Purchase date cannot "
                    "be in the future"
                )

        return None