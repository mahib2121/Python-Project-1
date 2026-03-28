"""
storage.py – JSON-based persistence layer.
"""

from __future__ import annotations
import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from expense import Expense


class JSONStorage:

    def __init__(self, filepath: str = "data/expenses.json") -> None:
        self.filepath = filepath
        self._ensure_file_exists()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_file_exists(self) -> None:
        directory = os.path.dirname(self.filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as fh:
                json.dump([], fh)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> list[dict]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    return data
                return []
        except (json.JSONDecodeError, OSError):
            return []

    def save_all(self, expenses: list["Expense"]) -> None:
        records = [exp.to_dict() for exp in expenses]
        with open(self.filepath, "w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2, ensure_ascii=False)

    def get_filepath(self) -> str:
        return os.path.abspath(self.filepath)
