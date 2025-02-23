import os
import glob
import json
from datetime import datetime

# Directory containing JSON files
json_dir = "results/"

# Words to filter out (case-insensitive)
bad_words = ["book", "document", "section", "chapter", "figure"]

merged_entries = []

# Loop over all JSON files in the directory
for filepath in glob.glob(os.path.join(json_dir, "*.json")):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {filepath}: {e}")
            continue

        # Assume that each JSON file is a list of entries
        if isinstance(data, list):
            for entry in data:
                # Convert the entry to a string and make it lowercase for checking
                entry_str = str(entry).lower()
                if any(bad_word in entry_str for bad_word in bad_words):
                    continue  # Skip this entry if it contains any bad word
                merged_entries.append(entry)
        else:
            # If the JSON file is a single JSON object, check it directly
            entry_str = str(data).lower()
            if not any(bad_word in entry_str for bad_word in bad_words):
                merged_entries.append(data)

# Generate a filename with current date and time
output_filename = f"results/merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Write the merged entries to the new JSON file
with open(output_filename, "w", encoding="utf-8") as outfile:
    json.dump(merged_entries, outfile, indent=4)

print(f"Merged JSON saved to {output_filename}")
