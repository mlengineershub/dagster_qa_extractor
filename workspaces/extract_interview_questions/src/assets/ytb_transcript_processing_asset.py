from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
from dagster import asset, AssetExecutionContext, Config
from typing import List, Dict, Generator
from io import StringIO
from src.resources.ollama_ressource import OllamaResource
from src.assets import utils


class ExtractTranscriptConfig(Config):
    video_id: str


def get_transcript(config: ExtractTranscriptConfig) -> Generator[str, None, None]:
    """Yields transcript text entry by entry."""
    video_id = "LPZh9BOjkQs"
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    for entry in transcript:
        yield entry["text"]


def stream_transcript_chunks(
    transcript: Generator[str, None, None], buffer_size: int = 1000
) -> Generator[str, None, None]:
    """Accumulates transcript text and yields it in fixed-size chunks."""
    buffer = StringIO()

    for text in transcript:
        buffer.write(text + " ")

        while buffer.tell() >= buffer_size:
            buffer.seek(0)
            yield buffer.read(buffer_size)
            remaining_text = buffer.read()
            buffer = StringIO(remaining_text)

    buffer.seek(0)
    leftover = buffer.read().strip()
    if leftover:
        yield leftover


@asset(required_resource_keys={"ollama_resource"})
def extract_entries(
    context: AssetExecutionContext, config: ExtractTranscriptConfig
) -> List[Dict[str, str]]:
    ollama_resource: OllamaResource = context.resources.ollama_resource
    entities: List[Dict[str, str]] = []
    for text in stream_transcript_chunks(get_transcript(config)):
        if text:
            # Sanitize text and retrieve additional context from the vector store
            text = utils.sanitize_text(text)
            system_prompt = "You are a precise and very efficient knowledge extractor and formatter."
            # Build the prompt for extraction
            prompt = (
                "Extract different questions and answers from the following text of a video transcript about Generative AI. "
                "The questions should not be general; they should be specific and well explained for the reader to answer smoothly. "
                "The questions should be long enough and should not be too short and summarized. "
                "The questions should not mention 'this section', 'this book','this context' and 'Figure'. "
                "Avoid Talking about Figures, Tables, and References. "
                "Avoid talking about the author and the book itself. "
                "Avoid talking about the structure of the book. "
                "An example of a question: 'How do generative multimodal models differ from language models?'. "
                "The answers should rely mostly on the text provided and your knowledge. "
                "The answer should not contain phrases like 'this text' or 'this context'—answer directly. "
                "The question/answer pairs will serve to generate a consistent interview question database. "
                "The answer should be detailed!\n"
                "The answer should have a lot of details, long enough and informative just like an answer in an interview. "
                "The question/answer pair should be empty only when there is insufficient text to create qa pairs from it.\n"
                "The question/answer pair should be generated only from the text provided. "
                f"Section: {text}"
            )
            try:
                # Use the ollama_resource to generate completions
                list_entries = ollama_resource.generate_completion(
                    system_prompt=system_prompt,
                    user_prompt=prompt,
                    model_name="llama3.2:3b",
                )
                generated_entries = utils.entries_to_json(list_entries.entries)
                entities.extend(generated_entries)
            except Exception as e:
                context.log.error(f"Error : {e}")
        else:
            context.log.info("No extractable text.")
    return entities
