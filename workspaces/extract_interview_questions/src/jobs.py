import os
from typing import List, Dict
from dagster import op, job, OpExecutionContext, build_asset_context
from src.assets.text_processing_asset import extract_entries, ExtractEntriesConfig
from src.resources.ollama_ressource import OllamaResource


@op(required_resource_keys={"ollama_resource"})
def process_all_pdfs_op(context: OpExecutionContext) -> List[List[Dict[str, str]]]:
    """
    Lists all PDF files in the "data" directory, processes each by calling the
    extract_entries asset with starting_page=0, and aggregates the results.
    """
    directory: str = "data"
    try:
        files: List[str] = os.listdir(directory)
    except Exception as e:
        context.log.error(f"Error listing directory '{directory}': {e}")
        return []

    pdf_files: List[str] = [
        os.path.join(directory, f) for f in files if f.lower().endswith(".pdf")
    ]
    all_results: List[List[Dict[str, str]]] = []

    for pdf_file in pdf_files:
        config: ExtractEntriesConfig = ExtractEntriesConfig(
            pdf_path=pdf_file, starting_page=0
        )
        context.log.info(f"Processing '{pdf_file}' with starting_page=0")
        # Build an asset context using the resource from our op context.
        asset_context = build_asset_context(
            resources={"ollama_resource": context.resources.ollama_resource}
        )
        results: List[Dict[str, str]] = extract_entries(asset_context, config)  # type: ignore
        all_results.append(results)

    return all_results


@job(
    resource_defs={
        "ollama_resource": OllamaResource(model_name="llama3.2:3b", timeout=60.0)
    }
)
def process_all_pdfs():  # type: ignore
    process_all_pdfs_op()
