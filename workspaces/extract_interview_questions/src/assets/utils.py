import re
from src.resources.models import Entry
from typing import List, Dict
import json


def sanitize_json_string(json_str: str) -> str:
    return re.sub(r"\\x(?![0-9a-fA-F]{2})", r"\\x00", json_str)


def sanitize_text(text: str) -> str:
    return text.encode("utf-8", errors="replace").decode("utf-8")


def entries_to_json(entries: List[Entry]) -> List[Dict[str, str]]:
    return [{"question": entry.question, "answer": entry.answer} for entry in entries]


def write_entries(entries: List[Dict[str, str]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(entries, file, indent=2)