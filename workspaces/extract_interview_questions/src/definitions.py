from dagster import Definitions

from src.assets.transcript_processing_asset import extract_entries_transcript
from src.assets.text_processing_asset import extract_entries
from src.resources.ollama_ressource import OllamaResource
from src.jobs import process_all_pdfs

defs = Definitions(
    assets=[extract_entries, extract_entries_transcript],
    resources={
        "ollama_resource": OllamaResource(model_name="llama3.2:3b"),
    },
    jobs=[
        process_all_pdfs,
    ],
)
