import re
import json
import PyPDF2
import os
from typing import Any, List, Dict
from ollama import chat
from pydantic import BaseModel
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- Helper Functions and Models ---


def sanitize_json_string(json_str: str) -> str:
    sanitized = re.sub(r"\\x(?![0-9a-fA-F]{2})", r"\\x00", json_str)
    return sanitized


def sanitize_text(text: str) -> str:
    # Replace problematic Unicode surrogates by encoding with 'replace'
    return text.encode("utf-8", errors="replace").decode("utf-8")


class Entry(BaseModel):
    question: str
    answer: str


class ListEntries(BaseModel):
    entries: List[Entry]


def entries_to_json(entries: List[Entry]) -> List[Dict[str, str]]:
    return [{"question": entry.question, "answer": entry.answer} for entry in entries]


def initialize_vectordb(file_path: str) -> Chroma:
    name = file_path.split("/")[-1].split(".")[0].replace(" ", "_")
    persist_dir = f"./{name}"
    if os.path.exists(persist_dir):
        embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest")
        vector_store = Chroma(
            collection_name=name,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
        return vector_store
    else:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        all_splits = text_splitter.split_documents(docs)
        # Sanitize each document's content to avoid surrogate issues.
        for doc in all_splits:
            doc.page_content = sanitize_text(doc.page_content)
        embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest")
        vector_store = Chroma(
            collection_name=name,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
        _ = vector_store.add_documents(documents=all_splits)
        return vector_store


def retrieve_additional_context(page_text: str, vector_store: Chroma) -> Any:
    return vector_store.similarity_search(page_text)


def generate(section: str, additional_context: str) -> List[Entry]:
    prompt = (
        "You are a precise and very efficient knowledge extractor and formatter. "
        "Extract different questions and answers from the following text of a book about Generative AI. "
        "The questions should not be general; they should be specific and well explained for the reader to answer smoothly. "
        "The questions should be direct and should not mention 'this section' or 'this book' or 'this context'. "
        "An example of a question: 'How do generative multimodal models differ from language models?'. "
        "The answers should rely mostly on the text provided and your knowledge. "
        "The answer should not contain phrases like 'this text', 'this context', or any equivalent expression—answer directly. "
        "The question/answer pairs will serve to generate a consistent interview question database. "
        "The answer should be detailed!\n"
        "The question/answer pair should not be empty\n"
        f"Section: {section}\nAdditional context: {additional_context}"
    )

    response = chat(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="deepseek-r1:8b",
        format=ListEntries.model_json_schema(),
    )

    raw_json = response["message"]["content"]
    sanitized_json = sanitize_json_string(raw_json)

    try:
        parsed = json.loads(sanitized_json)
    except Exception as e:
        print("Error parsing JSON with json.loads:", e)
        print("Raw (sanitized) JSON content:", sanitized_json)
        raise e

    try:
        list_entries = ListEntries.parse_obj(parsed)
    except Exception as e:
        print("Pydantic validation error:", e)
        print("Parsed JSON object:", parsed)
        raise e

    return list_entries.entries


def write_entries(entries: List[Dict[str, str]], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(entries, file, indent=2)


def extract_entries_from_page(
    pdf_path: str, starting_page: int
) -> List[Dict[str, str]]:
    # Catch initialization errors (e.g. non-existent file) and return empty list
    try:
        vector_store = initialize_vectordb(pdf_path)
    except ValueError as ve:
        print(f"Error initializing vector DB: {ve}")
        return []

    entities: List[Dict[str, str]] = []
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            if starting_page < 0 or starting_page >= total_pages:
                print(
                    f"Invalid starting page: {starting_page}. The PDF has {total_pages} pages."
                )
                return []

            for page_num in range(starting_page, total_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    # Sanitize page text to handle surrogate characters.
                    page_text = sanitize_text(page_text)
                    additional_context = retrieve_additional_context(
                        page_text, vector_store
                    )
                    try:
                        generated_entries = entries_to_json(
                            generate(page_text, additional_context)
                        )
                        print(f"Entries from page {page_num + 1}:", generated_entries)
                        entities.extend(generated_entries)
                    except Exception as e:
                        print(f"Error processing page {page_num + 1}: {e}")
                else:
                    print(f"No extractable text on page {page_num + 1}.")

                write_entries(entities, filename="test.json")
    except Exception as e:
        print(f"Error reading file {pdf_path}: {e}")
        return []
    return entities
