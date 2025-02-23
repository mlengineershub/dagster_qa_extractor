from dagster import Definitions

from src.assets.text_processing_asset import extract_entries
from src.resources.openai_ressource import OpenAIResource
from src.jobs import process_all_pdfs
import os
from dotenv import load_dotenv

load_dotenv()
model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")

defs = Definitions(
    assets=[
        extract_entries,
    ],
    resources={
        "openai_resource": OpenAIResource(model_name=model_name),
    },
    jobs=[
        process_all_pdfs,
    ],
)
