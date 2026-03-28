"""
ui.py – PySimpleGUI/FreeSimpleGUI-based graphical interface.

"""

from __future__ import annotations
import sys
from datetime import date, datetime

try:
    import FreeSimpleGUI as sg
except ImportError:
    try:
        import PySimpleGUI as sg
    except ImportError:
        print("ERROR: Could not import FreeSimpleGUI or PySimpleGUI.")
        print("Please activate your virtual environment and run:")
        print("  pip install FreeSimpleGUI")
        sys.exit(1)

from expense import VALID_CATEGORIES
from manager import ExpenseManager


# ---------------------------------------------------------------------------
# Theme & visual constants
# ---------------------------------------------------------------------------

THEME = "DarkBlue14"

HEADER_FONT = ("Segoe UI", 18, "bold")
LABEL_FONT = ("Segoe UI", 10)
TABLE_FONT = ("Consolas", 10)

COL_WIDTHS = [36, 12, 18, 12, 28]  # title, amount, category, date, note
TABLE_HEADINGS = ["Title", "Amount (৳)", "Category", "Date", "Note"]

SORT_OPTIONS = ["Date", "Amount", "Title", "Category"]
FILTER_OPTIONS = ["All"] + VALID_CATEGORIES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def today_str() -> str:
    """Return today's date as a YYYY-MM-DD string."""
    return date.today().isoformat()


def expense_to_row(exp) -> list:
    """Convert an Expense object to a display row for the table."""
    return [
        exp.title,
        f"৳{exp.amount:,.2f}",
        exp.category,
        exp.date,
        exp.note or "—",
    ]


def popup_error(msg: str) -> None:
    """Show a modal error popup."""
    sg.popup_error(msg, title="Validation Error", keep_on_top=True)


def popup_ok(msg: str) -> None:
    """Show a confirmation popup."""
    sg.popup_ok(msg, title="Success", keep_on_top=True)


# ---------------------------------------------------------------------------
# Dialog windows
# ---------------------------------------------------------------------------


def expense_form_window(
    title_win: str = "Add Expense",
    defaults: dict | None = None,
) -> dict | None:

    d = defaults or {}
    layout = [
        [
            sg.Text("Title *", font=LABEL_FONT, size=(10, 1)),
            sg.Input(d.get("title", ""), key="-TITLE-", size=(35, 1)),
        ],
        [
            sg.Text("Amount (৳) *", font=LABEL_FONT, size=(10, 1)),
            sg.Input(d.get("amount", ""), key="-AMOUNT-", size=(15, 1)),
        ],
        [
            sg.Text("Category *", font=LABEL_FONT, size=(10, 1)),
            sg.Combo(
                VALID_CATEGORIES,
                default_value=d.get("category", VALID_CATEGORIES[0]),
                key="-CATEGORY-",
                readonly=True,
                size=(22, 1),
            ),
        ],
        [
            sg.Text("Date *", font=LABEL_FONT, size=(10, 1)),
            sg.Input(d.get("date", today_str()), key="-DATE-", size=(14, 1)),
            sg.CalendarButton(
                "📅",
                target="-DATE-",
                format="%Y-%m-%d",
                begin_at_sunday_plus=1,
                no_titlebar=False,
                title="Pick a date",
            ),
        ],
        [
            sg.Text("Note", font=LABEL_FONT, size=(10, 1)),
            sg.Input(d.get("note", ""), key="-NOTE-", size=(35, 1)),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Push(),
            sg.Button(
                "Save", key="-SAVE-", button_color=("white", "#2E86AB"), size=(10, 1)
            ),
            sg.Button("Cancel", key="-CANCEL-", size=(10, 1)),
            sg.Push(),
        ],
    ]
    window = sg.Window(title_win, layout, modal=True, finalize=True)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "-CANCEL-"):
            window.close()
            return None
        if event == "-SAVE-":
            window.close()
            return values


def report_window(manager: ExpenseManager, filtered_expenses=None) -> None:
    target = filtered_expenses if filtered_expenses is not None else manager.get_all()

    total = manager.report_total(target)
    avg = manager.report_average(target)
    by_cat = manager.report_by_category(target)
    monthly = manager.report_monthly(target)
    top5 = manager.report_top_n(5, target)

    # Build category rows
    cat_rows = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
    cat_table = [[cat, f"৳{amt:,.2f}"] for cat, amt in cat_rows]

    # Build monthly rows
    month_table = [[m, f"৳{amt:,.2f}"] for m, amt in monthly.items()]

    # Build top-5 rows
    top5_table = [[e.title, f"৳{e.amount:,.2f}", e.category, e.date] for e in top5]

    layout = [
        [sg.Text("📊  Expense Summary Report", font=HEADER_FONT)],
        [sg.HorizontalSeparator()],
        [
            sg.Text(f"  Total Expenses: {len(target)}", font=LABEL_FONT),
            sg.Push(),
            sg.Text(f"Total Spend: ৳{total:,.2f}", font=("Segoe UI", 11, "bold")),
            sg.Push(),
            sg.Text(f"Average: ৳{avg:,.2f}", font=LABEL_FONT),
        ],
        [sg.HorizontalSeparator()],
        [sg.Text("By Category", font=("Segoe UI", 11, "bold"))],
        [
            sg.Table(
                cat_table,
                headings=["Category", "Total"],
                col_widths=[25, 14],
                auto_size_columns=False,
                num_rows=min(8, len(cat_table) or 1),
                key="-CAT-TABLE-",
                font=TABLE_FONT,
                alternating_row_color="#1a2433",
            )
        ],
        [sg.Text("Monthly Totals", font=("Segoe UI", 11, "bold"))],
        [
            sg.Table(
                month_table,
                headings=["Month", "Total"],
                col_widths=[12, 14],
                auto_size_columns=False,
                num_rows=min(6, len(month_table) or 1),
                key="-MONTH-TABLE-",
                font=TABLE_FONT,
                alternating_row_color="#1a2433",
            )
        ],
        [sg.Text("Top 5 Most Expensive", font=("Segoe UI", 11, "bold"))],
        [
            sg.Table(
                top5_table,
                headings=["Title", "Amount", "Category", "Date"],
                col_widths=[28, 13, 18, 12],
                auto_size_columns=False,
                num_rows=min(5, len(top5_table) or 1),
                key="-TOP5-TABLE-",
                font=TABLE_FONT,
                alternating_row_color="#1a2433",
            )
        ],
        [sg.Push(), sg.Button("Close", size=(10, 1)), sg.Push()],
    ]

    window = sg.Window("Summary Report", layout, modal=True, finalize=True)
    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, "Close"):
            break
    window.close()


# ---------------------------------------------------------------------------
# Main application window
# ---------------------------------------------------------------------------


class ExpenseTrackerApp:
    def __init__(self) -> None:
        self._manager = ExpenseManager()
        self._current_list: list = []  # expenses currently shown in table
        self._id_map: list[str] = []  # parallel list of IDs for the displayed rows

        sg.theme(THEME)
        self._window = self._build_window()

    # ------------------------------------------------------------------
    # Layout builder
    # ------------------------------------------------------------------

    def _build_window(self) -> sg.Window:

        # ── Top toolbar ──────────────────────────────────────────────
        toolbar = [
            sg.Button(
                "➕  Add", key="-ADD-", button_color=("white", "#27AE60"), size=(10, 1)
            ),
            sg.Button(
                "✏️  Edit", key="-EDIT-", button_color=("white", "#2980B9"), size=(10, 1)
            ),
            sg.Button(
                "🗑️  Delete",
                key="-DELETE-",
                button_color=("white", "#C0392B"),
                size=(10, 1),
            ),
            sg.VerticalSeparator(),
            sg.Button(
                "📊  Report",
                key="-REPORT-",
                button_color=("white", "#8E44AD"),
                size=(11, 1),
            ),
            sg.Push(),
            sg.Button("🔄  Refresh", key="-REFRESH-", size=(11, 1)),
        ]

        # ── Search & filter bar ──────────────────────────────────────
        search_bar = [
            sg.Text("🔍 Search:", font=LABEL_FONT),
            sg.Input("", key="-SEARCH-", size=(22, 1), enable_events=True),
            sg.Text("  Category:", font=LABEL_FONT),
            sg.Combo(
                FILTER_OPTIONS,
                default_value="All",
                key="-FILTER-CAT-",
                readonly=True,
                size=(18, 1),
                enable_events=True,
            ),
            sg.Text("  Sort by:", font=LABEL_FONT),
            sg.Combo(
                SORT_OPTIONS,
                default_value="Date",
                key="-SORT-",
                readonly=True,
                size=(10, 1),
                enable_events=True,
            ),
            sg.Checkbox("Desc", default=True, key="-DESC-", enable_events=True),
        ]

        # ── Date-range filter ────────────────────────────────────────
        date_filter = [
            sg.Text("From:", font=LABEL_FONT),
            sg.Input("", key="-FROM-", size=(12, 1)),
            sg.CalendarButton(
                "📅", target="-FROM-", format="%Y-%m-%d", title="From date"
            ),
            sg.Text("  To:", font=LABEL_FONT),
            sg.Input("", key="-TO-", size=(12, 1)),
            sg.CalendarButton("📅", target="-TO-", format="%Y-%m-%d", title="To date"),
            sg.Button("Apply Range", key="-APPLY-RANGE-", size=(11, 1)),
            sg.Button("Clear Range", key="-CLEAR-RANGE-", size=(11, 1)),
        ]

        # ── Expense table ────────────────────────────────────────────
        table = sg.Table(
            values=[],
            headings=TABLE_HEADINGS,
            col_widths=COL_WIDTHS,
            auto_size_columns=False,
            num_rows=18,
            key="-TABLE-",
            font=TABLE_FONT,
            alternating_row_color="#1a2433",
            enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            justification="left",
            expand_x=True,
            expand_y=True,
        )

        # ── Status bar ───────────────────────────────────────────────
        status_bar = [
            sg.Text("", key="-STATUS-", font=LABEL_FONT, size=(60, 1)),
            sg.Push(),
            sg.Text("", key="-TOTAL-", font=("Segoe UI", 11, "bold")),
        ]

        layout = [
            [sg.Text("💰  Personal Expense Tracker", font=HEADER_FONT, pad=(10, 10))],
            [sg.HorizontalSeparator()],
            toolbar,
            [sg.HorizontalSeparator()],
            search_bar,
            date_filter,
            [sg.HorizontalSeparator()],
            [table],
            [sg.HorizontalSeparator()],
            status_bar,
        ]

        return sg.Window(
            "Personal Expense Tracker",
            layout,
            size=(1000, 700),
            resizable=True,
            finalize=True,
        )

    # ------------------------------------------------------------------
    # Table helpers
    # ------------------------------------------------------------------

    def _refresh_table(self, expenses=None) -> None:
        """Re-populate the table from the given expense list."""
        if expenses is None:
            expenses = self._manager.get_all()
        self._current_list = expenses
        self._id_map = [e.id for e in expenses]
        rows = [expense_to_row(e) for e in expenses]
        self._window["-TABLE-"].update(values=rows)
        total = self._manager.report_total(expenses)
        count = len(expenses)
        self._window["-STATUS-"].update(f"{count} record(s) shown")
        self._window["-TOTAL-"].update(f"Total: ৳{total:,.2f}")

    def _get_selected_id(self, values: dict) -> str | None:
        """Return the expense ID of the currently selected table row."""
        selected = values.get("-TABLE-")
        if not selected:
            return None
        idx = selected[0]
        if idx >= len(self._id_map):
            return None
        return self._id_map[idx]

    def _apply_filters(self, values: dict) -> list:

        query = values.get("-SEARCH-", "").strip()
        cat = values.get("-FILTER-CAT-", "All")
        sort_key = values.get("-SORT-", "Date").lower()
        descend = values.get("-DESC-", True)

        expenses = self._manager.search(query)
        if cat and cat != "All":
            expenses = [e for e in expenses if e.category == cat]
        expenses = self._manager.sort(expenses, key=sort_key, reverse=descend)
        return expenses

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _handle_add(self) -> None:

        result = expense_form_window("Add Expense")
        if result is None:
            return
        errors = __import__("expense").Expense.validate(
            result["-TITLE-"],
            result["-AMOUNT-"],
            result["-CATEGORY-"],
            result["-DATE-"],
        )
        if errors:
            popup_error("\n".join(errors))
            return
        self._manager.add(
            title=result["-TITLE-"],
            amount=float(result["-AMOUNT-"]),
            category=result["-CATEGORY-"],
            expense_date=result["-DATE-"],
            note=result["-NOTE-"],
        )

    def _handle_edit(self, values: dict) -> None:

        expense_id = self._get_selected_id(values)
        if not expense_id:
            popup_error("Please select a record to edit.")
            return
        exp = self._manager.get_by_id(expense_id)
        if exp is None:
            popup_error("Record not found.")
            return
        defaults = {
            "title": exp.title,
            "amount": str(exp.amount),
            "category": exp.category,
            "date": exp.date,
            "note": exp.note,
        }
        result = expense_form_window("Edit Expense", defaults=defaults)
        if result is None:
            return
        errors = __import__("expense").Expense.validate(
            result["-TITLE-"],
            result["-AMOUNT-"],
            result["-CATEGORY-"],
            result["-DATE-"],
        )
        if errors:
            popup_error("\n".join(errors))
            return
        self._manager.update(
            expense_id=expense_id,
            title=result["-TITLE-"],
            amount=float(result["-AMOUNT-"]),
            category=result["-CATEGORY-"],
            expense_date=result["-DATE-"],
            note=result["-NOTE-"],
        )

    def _handle_delete(self, values: dict) -> None:
        expense_id = self._get_selected_id(values)
        if not expense_id:
            popup_error("Please select a record to delete.")
            return
        exp = self._manager.get_by_id(expense_id)
        confirm = sg.popup_yes_no(
            f"Delete '{exp.title}' (৳{exp.amount:,.2f})?\nThis cannot be undone.",
            title="Confirm Delete",
            keep_on_top=True,
        )
        if confirm == "Yes":
            self._manager.delete(expense_id)

    def _handle_date_range(self, values: dict) -> list | None:
        """Apply the date-range filter and return the filtered list."""
        start = values.get("-FROM-", "").strip()
        end = values.get("-TO-", "").strip()
        if not start or not end:
            popup_error("Please enter both From and To dates.")
            return None
        return self._manager.filter_by_date_range(start, end)

    # ------------------------------------------------------------------
    # Main event loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Start the event loop and block until the window is closed."""
        self._refresh_table()

        while True:
            event, values = self._window.read()

            if event == sg.WIN_CLOSED:
                break

            # ── CRUD buttons ─────────────────────────────────────────
            elif event == "-ADD-":
                self._handle_add()
                self._refresh_table(self._apply_filters(values))

            elif event == "-EDIT-":
                self._handle_edit(values)
                self._refresh_table(self._apply_filters(values))

            elif event == "-DELETE-":
                self._handle_delete(values)
                self._refresh_table(self._apply_filters(values))

            # ── Report ───────────────────────────────────────────────
            elif event == "-REPORT-":
                report_window(self._manager, self._current_list)

            # ── Search / filter / sort (live updates) ────────────────
            elif event in ("-SEARCH-", "-FILTER-CAT-", "-SORT-", "-DESC-"):
                self._refresh_table(self._apply_filters(values))

            # ── Date range ───────────────────────────────────────────
            elif event == "-APPLY-RANGE-":
                result = self._handle_date_range(values)
                if result is not None:
                    # Also apply existing search/sort on top of range filter
                    query = values.get("-SEARCH-", "").strip()
                    cat = values.get("-FILTER-CAT-", "All")
                    sort_key = values.get("-SORT-", "Date").lower()
                    descend = values.get("-DESC-", True)
                    if query:
                        result = [
                            e
                            for e in result
                            if query in e.title.lower()
                            or query in e.category.lower()
                            or query in e.note.lower()
                        ]
                    if cat and cat != "All":
                        result = [e for e in result if e.category == cat]
                    result = self._manager.sort(result, key=sort_key, reverse=descend)
                    self._refresh_table(result)

            elif event == "-CLEAR-RANGE-":
                self._window["-FROM-"].update("")
                self._window["-TO-"].update("")
                self._refresh_table(self._apply_filters(values))

            elif event == "-REFRESH-":
                self._refresh_table(self._apply_filters(values))

        self._window.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Application entry point."""
    app = ExpenseTrackerApp()
    app.run()


if __name__ == "__main__":
    main()
