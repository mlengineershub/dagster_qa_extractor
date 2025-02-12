from workspace.src.extract_entities import extract_entries_from_page, write_entries

pdf_path = "data/test_book.pdf"
entities = extract_entries_from_page(pdf_path, starting_page=0)
write_entries(entities, filename="results/test_book-extracted_entities.json")
print("Extraction complete. JSON file saved.")
