import json
import os
import tempfile
from workspace.src.extract_entities import (
    entries_to_json,
    write_entries,
    extract_entries_from_page,
    Entry,
)


def test_entries_to_json() -> None:
    entries = [{"question": "Q1", "answer": "A1"}]
    # Convert dictionaries to Entry objects
    entry_objs = [Entry(**entry) for entry in entries]
    result = entries_to_json(entry_objs)
    assert isinstance(result, list)
    assert isinstance(result[0], dict)
    assert "question" in result[0]
    assert "answer" in result[0]


def test_write_entries() -> None:
    entries = [{"question": "Q2", "answer": "A2"}]
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8") as tmp:
        tmp_filename = tmp.name
    try:
        write_entries(entries, filename=tmp_filename)
        with open(tmp_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list)
    finally:
        os.remove(tmp_filename)


def test_extract_entries_from_page() -> None:
    # For testing, call extract_entries_from_page on a non-existent PDF.
    # Expect an empty list.
    pdf_path = "data/this_is_an_erroneous_pdf.pdf"
    result = extract_entries_from_page(pdf_path, starting_page=0)
    assert result == [] or result is None  # Depending on error handling
