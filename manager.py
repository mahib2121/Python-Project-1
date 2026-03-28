"""
manager.py – ExpenseManager service class.

Contains all business logic: CRUD operations, search, sorting, filtering,
and summary report generation. Composes a JSONStorage instance for
persistence.
"""

from __future__ import annotations
from datetime import date
from collections import defaultdict

from expense import Expense, VALID_CATEGORIES
from storage import JSONStorage


class ExpenseManager:
    """
    Service / manager layer for expense operations.
    """

    def __init__(self, storage: JSONStorage | None = None) -> None:
        # Use provided storage or create default JSON storage
        self._storage: JSONStorage = storage or JSONStorage()

        # In-memory expense list
        self._expenses: list[Expense] = []

        self._load()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        """Load expenses from storage into memory."""
        raw = self._storage.load_all()
        self._expenses = []
        for record in raw:
            try:
                self._expenses.append(Expense.from_dict(record))
            except (KeyError, ValueError):
                # Skip invalid/corrupt data
                continue

    def _save(self) -> None:
        """Save current expense list to storage."""
        self._storage.save_all(self._expenses)

    def _find_by_id(self, expense_id: str) -> Expense | None:
        """Find expense by unique ID."""
        for exp in self._expenses:
            if exp.id == expense_id:
                return exp
        return None

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def add(
        self,
        title: str,
        amount: float,
        category: str,
        expense_date: str,
        note: str = "",
    ) -> Expense:
        """Create new expense and persist it."""
        exp = Expense(
            title=title,
            amount=float(amount),
            category=category,
            expense_date=expense_date,
            note=note,
        )
        self._expenses.append(exp)
        self._save()
        return exp

    def update(
        self,
        expense_id: str,
        title: str,
        amount: float,
        category: str,
        expense_date: str,
        note: str = "",
    ) -> bool:
        """Update existing expense by ID."""
        exp = self._find_by_id(expense_id)
        if exp is None:
            return False

        # Update fields
        exp.title = title.strip()
        exp.amount = float(amount)
        exp.category = category
        exp.date = expense_date
        exp.note = note.strip()

        self._save()
        return True

    def delete(self, expense_id: str) -> bool:
        """Delete expense by ID."""
        original_count = len(self._expenses)

        # Remove matching expense
        self._expenses = [e for e in self._expenses if e.id != expense_id]

        if len(self._expenses) < original_count:
            self._save()
            return True
        return False

    def get_all(self) -> list[Expense]:
        """Return all expenses (copy)."""
        return list(self._expenses)

    def get_by_id(self, expense_id: str) -> Expense | None:
        """Get single expense by ID."""
        return self._find_by_id(expense_id)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str) -> list[Expense]:
        """Search in title, category, and note (case-insensitive)."""
        query = query.strip().lower()
        if not query:
            return self.get_all()

        return [
            exp
            for exp in self._expenses
            if query in exp.title.lower()
            or query in exp.category.lower()
            or query in exp.note.lower()
        ]

    # ------------------------------------------------------------------
    # Sort / Filter
    # ------------------------------------------------------------------

    def filter_by_category(self, category: str) -> list[Expense]:
        """Filter expenses by category."""
        if not category or category == "All":
            return self.get_all()
        return [e for e in self._expenses if e.category == category]

    def filter_by_date_range(self, start: str, end: str) -> list[Expense]:
        """Filter expenses within date range (inclusive)."""
        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
        except ValueError:
            return self.get_all()

        return [
            e
            for e in self._expenses
            if start_date <= date.fromisoformat(e.date) <= end_date
        ]

    def sort(
        self, expenses: list[Expense], key: str = "date", reverse: bool = True
    ) -> list[Expense]:
        """Sort expenses by given key."""
        # Sorting rules mapping
        sort_keys = {
            "date": lambda e: e.date,
            "amount": lambda e: e.amount,
            "title": lambda e: e.title.lower(),
            "category": lambda e: e.category.lower(),
        }

        key_fn = sort_keys.get(key, sort_keys["date"])
        return sorted(expenses, key=key_fn, reverse=reverse)

    # ------------------------------------------------------------------
    # Summary Reports
    # ------------------------------------------------------------------

    def report_total(self, expenses: list[Expense] | None = None) -> float:
        """Calculate total expense amount."""
        target = expenses if expenses is not None else self._expenses
        return sum(e.amount for e in target)

    def report_average(self, expenses: list[Expense] | None = None) -> float:
        """Calculate average expense amount."""
        target = expenses if expenses is not None else self._expenses
        if not target:
            return 0.0
        return sum(e.amount for e in target) / len(target)

    def report_by_category(
        self, expenses: list[Expense] | None = None
    ) -> dict[str, float]:
        """Total spending grouped by category."""
        target = expenses if expenses is not None else self._expenses

        # defaultdict helps accumulate totals easily
        totals: dict[str, float] = defaultdict(float)
        for e in target:
            totals[e.category] += e.amount

        return dict(totals)

    def report_top_n(
        self, n: int = 5, expenses: list[Expense] | None = None
    ) -> list[Expense]:
        """Top N highest expenses."""
        target = expenses if expenses is not None else self._expenses
        return sorted(target, key=lambda e: e.amount, reverse=True)[:n]

    def report_monthly(self, expenses: list[Expense] | None = None) -> dict[str, float]:
        """Monthly expense summary (YYYY-MM)."""
        target = expenses if expenses is not None else self._expenses

        monthly: dict[str, float] = defaultdict(float)
        for e in target:
            # Extract month from date string
            month_key = e.date[:7]
            monthly[month_key] += e.amount

        return dict(sorted(monthly.items()))
