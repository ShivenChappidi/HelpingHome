"""
Create caretaker notes from a daily CSV using the Opennote API.

Usage:
  python -m opennote.daily_notes_from_csv --csv path/to/file.csv --date 2026-01-17
  python -m opennote.daily_notes_from_csv --csv path/to/file.csv --dry-run
"""

import argparse
import csv
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Tuple

from .client import OpenNoteService


DATE_COLUMNS = ("date", "day", "timestamp")
TITLE_COLUMNS = ("title", "subject")
NOTE_COLUMNS = ("note", "notes", "message", "details", "summary")
ROOM_COLUMNS = ("room", "area", "location")


def _parse_date(value: str) -> Optional[date]:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _pick_column(row: Dict[str, str], candidates: Iterable[str]) -> Optional[str]:
    for key in candidates:
        if key in row and row[key].strip():
            return row[key].strip()
    return None


def _collect_rows(csv_path: str, target_day: date) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            raw_date = _pick_column(row, DATE_COLUMNS)
            row_date = _parse_date(raw_date or "")
            if row_date == target_day:
                rows.append({k.strip(): (v or "").strip() for k, v in row.items()})
    return rows


def _format_note(rows: List[Dict[str, str]], target_day: date) -> Tuple[str, str]:
    title = f"Caretaker Notes - {target_day.isoformat()}"
    lines = [f"Date: {target_day.isoformat()}", ""]
    for idx, row in enumerate(rows, start=1):
        row_title = _pick_column(row, TITLE_COLUMNS) or f"Entry {idx}"
        room = _pick_column(row, ROOM_COLUMNS)
        note = _pick_column(row, NOTE_COLUMNS) or "No details provided."
        if room:
            lines.append(f"- {row_title} ({room}): {note}")
        else:
            lines.append(f"- {row_title}: {note}")
    return title, "\n".join(lines)


def _format_row_note(row: Dict[str, str], target_day: date, index: int) -> Tuple[str, str]:
    row_title = _pick_column(row, TITLE_COLUMNS) or f"Entry {index}"
    room = _pick_column(row, ROOM_COLUMNS)
    note = _pick_column(row, NOTE_COLUMNS) or "No details provided."
    title = f"Caretaker Note - {target_day.isoformat()} - {row_title}"
    lines = [f"Date: {target_day.isoformat()}"]
    if room:
        lines.append(f"Room: {room}")
    lines.append("")
    lines.append(note)
    return title, "\n".join(lines)


def _create_note(service: OpenNoteService, title: str, content: str):
    client = service.client
    if hasattr(client, "notes") and hasattr(client.notes, "create"):
        return client.notes.create(title=title, content=content)
    if hasattr(client, "note") and hasattr(client.note, "create"):
        return client.note.create(title=title, content=content)
    if hasattr(client, "create_note"):
        return client.create_note(title=title, content=content)
    raise AttributeError("Opennote client does not support note creation.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create caretaker notes from a daily CSV.")
    parser.add_argument("--csv", required=True, help="Path to CSV file.")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--dry-run", action="store_true", help="Print note without creating it.")
    parser.add_argument("--per-row", action="store_true", help="Create one note per CSV row.")
    args = parser.parse_args()

    target_day = _parse_date(args.date) if args.date else date.today()
    if target_day is None:
        raise SystemExit("Invalid --date format. Use YYYY-MM-DD.")

    rows = _collect_rows(args.csv, target_day)
    if not rows:
        print(f"No rows found for {target_day.isoformat()}.")
        return

    service = None if args.dry_run else OpenNoteService()

    if args.per_row:
        for index, row in enumerate(rows, start=1):
            title, content = _format_row_note(row, target_day, index)
            if args.dry_run:
                print(title)
                print(content)
                print("-" * 40)
                continue
            response = _create_note(service, title, content)
            print(f"✅ Note created: {title}")
            print(response)
        return

    title, content = _format_note(rows, target_day)
    if args.dry_run:
        print(title)
        print(content)
        return

    response = _create_note(service, title, content)
    print("✅ Note created.")
    print(response)


if __name__ == "__main__":
    main()