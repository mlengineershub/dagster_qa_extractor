import os
import csv
from typing import List, Dict
from dagster import op, job, OpExecutionContext, build_asset_context
from src.assets.text_processing_asset import extract_entries, ExtractEntriesConfig
from src.assets.transcript_processing_asset import (
    extract_entries_transcript,
    ExtractTranscriptConfig,
)
from src.resources.openai_ressource import OpenAIResource
from dotenv import load_dotenv

load_dotenv()
model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")


@op(required_resource_keys={"openai_resource"})
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
            resources={"openai_resource": context.resources.openai_resource}
        )
        results: List[Dict[str, str]] = extract_entries(asset_context, config)  # type: ignore
        all_results.append(results)

    return all_results


@op(required_resource_keys={"openai_resource"})
def process_all_videos_op(context: OpExecutionContext) -> List[List[Dict[str, str]]]:
    """
    processes each video in the videos.csv file by calling the extract_entries_transcript asset
    """
    path: str = "data/videos.csv"
    all_results: List[List[Dict[str, str]]] = []
    try:
        with open(path, newline="") as videos:
            video_reader = csv.reader(videos)
            for row in video_reader:
                config: ExtractTranscriptConfig = ExtractTranscriptConfig(
                    video_id="".join(row)
                )
                asset_context = build_asset_context(
                    resources={"openai_resource": context.resources.openai_resource}
                )
                results: List[Dict[str, str]] = extract_entries_transcript(
                    asset_context, config
                )  # type: ignore
                all_results.append(results)
    except Exception as e:
        context.log.info(f"Error while processing videos csv file: {e}")
    return all_results


@job(
    resource_defs={
        "openai_resource": OpenAIResource(model_name=model_name, timeout=60.0)
    }
)
def process_all_pdfs():  # type: ignore
    process_all_pdfs_op()


@job(
    resource_defs={
        "openai_resource": OpenAIResource(model_name=model_name, timeout=60.0)
    }
)
def process_all_videos():  # type: ignore
    process_all_videos_op()
