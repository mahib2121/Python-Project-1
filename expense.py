"""
expense.py – Expense entity class.

"""

from __future__ import annotations
import uuid
from datetime import date


# Predefined valid categories (used for validation)
VALID_CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Entertainment",
    "Health",
    "Housing",
    "Education",
    "Travel",
    "Utilities",
    "Other",
]


class Expense:
    """
    Entity class representing a single expense.
    """

    def __init__(
        self,
        title: str,
        amount: float,
        category: str,
        expense_date: str,
        note: str = "",
        expense_id: str | None = None,
    ) -> None:
        """Create a new Expense, generating an ID if one is not supplied."""

        # Generate unique ID if not provided
        self.id: str = expense_id or str(uuid.uuid4())

        self.title: str = title.strip()
        self.amount: float = float(amount)
        self.category: str = category
        self.date: str = expense_date
        self.note: str = note.strip()

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a plain dict suitable for JSON serialisation."""
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """Reconstruct an Expense from stored dict (e.g., JSON load)."""
        return cls(
            title=data["title"],
            amount=data["amount"],
            category=data["category"],
            expense_date=data["date"],
            note=data.get("note", ""),
            expense_id=data["id"],
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate(
        title: str, amount_str: str, category: str, date_str: str
    ) -> list[str]:
        errors: list[str] = []

        if not title.strip():
            errors.append("Title cannot be empty.")

        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append("Amount must be greater than zero.")
        except (ValueError, TypeError):
            errors.append("Amount must be a valid number.")

        if category not in VALID_CATEGORIES:
            errors.append(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")

        try:
            date.fromisoformat(date_str)
        except ValueError:
            errors.append("Date must be in YYYY-MM-DD format.")

        return errors

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Expense(id={self.id!r}, title={self.title!r}, "
            f"amount={self.amount:.2f}, category={self.category!r}, date={self.date!r})"
        )
