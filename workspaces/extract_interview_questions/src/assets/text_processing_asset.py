import os
import PyPDF2
from dagster import asset, AssetExecutionContext, Config
from typing import Any, List, Dict
from src.resources.openai_ressource import OpenAIResource
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.assets import utils
from dotenv import load_dotenv
# --- Configuration ---

load_dotenv()


class ExtractEntriesConfig(Config):
    pdf_path: str
    starting_page: int


# --- Helper Functions and Models ---

def initialize_vectordb(file_path: str) -> Chroma:
    name = os.path.basename(file_path).split(".")[0].replace(" ", "_")
    persist_dir = f"./embedding_databases/{name}"
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
        for doc in all_splits:
            doc.page_content = utils.sanitize_text(doc.page_content)
        embeddings = OllamaEmbeddings(model="mxbai-embed-large:latest")
        vector_store = Chroma(
            collection_name=name,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
        _ = vector_store.add_documents(documents=all_splits)
        return vector_store


def retrieve_additional_context(page_text: str, vector_store: Chroma) -> Any:
    return vector_store.similarity_search(query=page_text, k=1)


# --- Dagster Asset Definition ---


@asset(required_resource_keys={"openai_resource"})
def extract_entries(
    context: AssetExecutionContext, config: ExtractEntriesConfig
) -> List[Dict[str, str]]:
    pdf_path = config.pdf_path
    starting_page = config.starting_page
    entities: List[Dict[str, str]] = []
    openai_resource: OpenAIResource = context.resources.openai_resource
    file_name = pdf_path.split("/")[-1].replace(".pdf", "")
    # try:
    #     vector_store = initialize_vectordb(pdf_path)
    # except Exception as e:
    #     context.log.error(f"Error initializing vector DB: {e}")
    #     return []

    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            if starting_page < 0 or starting_page >= total_pages:
                context.log.error(
                    f"Invalid starting page: {starting_page}. The PDF has {total_pages} pages."
                )
                return []
            for page_num in range(starting_page, total_pages):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    # Sanitize text and retrieve additional context from the vector store
                    page_text = utils.sanitize_text(page_text)
                    # additional_context = retrieve_additional_context(page_text, vector_store)
                    system_prompt = "You are a precise and very efficient knowledge extractor and formatter. "
                    # Build the prompt for extraction
                    prompt = (
                        "Extract different questions and answers from the following text of a book about Generative AI. "
                        "The questions should not be general; they should be specific and well explained for the reader to answer smoothly. "
                        "The questions should be long enough and should not be too short and summarized. "
                        "The questions should not mention 'this section', 'this book','this context' and 'Figure'. "
                        "Avoid Talking about Figures, Tables, and References. "
                        "Avoid talking about the author and the book itself. "
                        "Avoid talking about the structure of the book. "
                        "The question should contain all the context needed to answer it, do not refer to the text, but instead add the context to the question from the text. "
                        "The answers should rely mostly on the text provided and your knowledge. "
                        "The answer should not contain phrases like 'this text' or 'this context'—answer directly. "
                        "The question/answer pairs will serve to generate a consistent interview question database. "
                        "The answer should be detailed!\n"
                        "The answer should have a lot of details, long enough and informative just like an answer in an interview. "
                        "The question/answer pair should be empty only when there is insufficient text to create qa pairs from it.\n"
                        "The question/answer pair should be generated only from the text provided. "
                        f"Section: {page_text}"
                        # f"Section: {page_text}\nAdditional context: {additional_context}"
                    )

                    try:
                        # Use the openai_resource to generate completions
                        model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
                        list_entries = openai_resource.generate_completion(
                            system_prompt=system_prompt,
                            user_prompt=prompt,
                            model_name=model_name,
                        )
                        generated_entries = utils.entries_to_json(list_entries.entries)
                        context.log.info(
                            f"Entries from page {page_num + 1}: {generated_entries}"
                        )
                        entities.extend(generated_entries)
                    except Exception as e:
                        context.log.error(f"Error processing page {page_num + 1}: {e}")
                else:
                    context.log.info(f"No extractable text on page {page_num + 1}.")

                # Optionally, write the accumulated entries to a file for inspection
                utils.write_entries(
                    entities, filename=f"results/{file_name}_extracted_entries.json"
                )
    except Exception as e:
        context.log.error(f"Error reading file {pdf_path}: {e}")
        return []

    return entities
