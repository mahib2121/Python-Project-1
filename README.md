# 💰 Personal Expense Tracker

A fully-featured desktop expense tracking application built with **Python** and **FreeSimpleGUI**.

---

## Features

| Feature                 | Details                                                                   |
| ----------------------- | ------------------------------------------------------------------------- |
| **Add / Edit / Delete** | Full CRUD with form validation                                            |
| **Live Search**         | Searches title, category, and notes simultaneously                        |
| **Category Filter**     | 10 built-in categories (Food, Transport, Shopping, …)                     |
| **Date Range Filter**   | Filter by any From–To date window                                         |
| **Sort**                | By Date, Amount, Title, or Category (asc/desc)                            |
| **Summary Report**      | Total spend, average, per-category breakdown, monthly totals, top-5 items |
| **Persistence**         | All data saved to `data/expenses.json` – survives restarts                |
| **Validation**          | Graceful error handling; no crashes on bad input                          |

---

## Project Structure

```
expense_tracker/
│
├── .venv/                  ← Virtual environment (not committed)
├── data/
│   └── expenses.json       ← Auto-created on first run
│
├── expense.py              ← Entity class (Expense + validation)
├── storage.py              ← JSONStorage – persistence layer
├── manager.py              ← ExpenseManager – business logic (CRUD, search, reports)
├── ui.py                   ← ExpenseTrackerApp – GUI controller
│
├── requirements.txt        ← External dependencies
└── README.md
```

### OOP Class Overview

```
Expense          (entity)      – represents one expense record
JSONStorage      (storage)     – reads/writes data/expenses.json
ExpenseManager   (service)     – CRUD, search, sort, filter, reports
                                 ↳ composes JSONStorage
ExpenseTrackerApp (UI/controller) – owns the PySimpleGUI window lifecycle
                                 ↳ composes ExpenseManager
```

---

## Setup & Run

### 1. Create and activate the virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python ui.py
```

---

## Requirements

- Python 3.10+
- No external GUI framework installation beyond `FreeSimpleGUI`
- `tkinter` must be available (ships with most Python installers)
  - Ubuntu/Debian: `sudo apt-get install python3-tk`

---

## Data file

Expenses are stored in `data/expenses.json` (created automatically).
You can back it up, share it, or edit it manually if needed.

Example record:

```json
{
  "id": "a1b2c3d4-...",
  "title": "Lunch at cafe",
  "amount": 350.0,
  "category": "Food & Dining",
  "date": "2025-03-15",
  "note": "Team lunch"
}
```
