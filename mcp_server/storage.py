"""
storage.py
----------
Local, file-based storage for deadlines.

Security notes:
- Data is stored ONLY on the local filesystem (data/deadlines.json).
  No external network calls are made from this module, which keeps
  personal task/deadline data private (relevant to the Concierge
  Agents track requirement of "keeping personal information safe").
- All reads/writes go through this module so validation is centralized
  in one place rather than scattered across tool handlers.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_FILE = DATA_DIR / "deadlines.json"

DATE_FORMAT = "%Y-%m-%d"


def _ensure_store() -> None:
    """Create the data directory/file if they don't exist yet."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps([]))


def _load() -> List[Dict]:
    _ensure_store()
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Fail safe: never crash the agent because of a corrupted file.
        return []


def _save(items: List[Dict]) -> None:
    _ensure_store()
    with open(DATA_FILE, "w") as f:
        json.dump(items, f, indent=2)


def _validate_date(date_str: str) -> Optional[str]:
    """Returns an error message if invalid, else None."""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return None
    except ValueError:
        return f"Invalid date '{date_str}'. Expected format YYYY-MM-DD."


def add_deadline(title: str, due_date: str, category: str = "general") -> Dict:
    """Add a new deadline. Returns the created record or an error dict."""
    title = (title or "").strip()
    if not title:
        return {"error": "Title cannot be empty."}
    if len(title) > 200:
        return {"error": "Title too long (max 200 characters)."}

    err = _validate_date(due_date)
    if err:
        return {"error": err}

    items = _load()
    record = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "due_date": due_date,
        "category": category.strip() or "general",
        "done": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    items.append(record)
    _save(items)
    return record


def list_deadlines(include_done: bool = False) -> List[Dict]:
    items = _load()
    if not include_done:
        items = [i for i in items if not i["done"]]
    return sorted(items, key=lambda x: x["due_date"])


def get_upcoming(days: int = 7) -> List[Dict]:
    """Return not-done deadlines due within `days` days from today (can include overdue)."""
    today = datetime.now().date()
    items = _load()
    result = []
    for item in items:
        if item["done"]:
            continue
        try:
            due = datetime.strptime(item["due_date"], DATE_FORMAT).date()
        except ValueError:
            continue
        delta = (due - today).days
        if delta <= days:
            item_copy = dict(item)
            item_copy["days_remaining"] = delta
            result.append(item_copy)
    return sorted(result, key=lambda x: x["days_remaining"])


def mark_done(deadline_id: str) -> Dict:
    items = _load()
    for item in items:
        if item["id"] == deadline_id:
            item["done"] = True
            _save(items)
            return item
    return {"error": f"No deadline found with id '{deadline_id}'."}


def delete_deadline(deadline_id: str) -> Dict:
    items = _load()
    new_items = [i for i in items if i["id"] != deadline_id]
    if len(new_items) == len(items):
        return {"error": f"No deadline found with id '{deadline_id}'."}
    _save(new_items)
    return {"success": True, "deleted_id": deadline_id}
