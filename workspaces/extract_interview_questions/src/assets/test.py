from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
from dagster import Config
from typing import Generator
from io import StringIO
from src.assets import utils


class ExtractTranscriptConfig(Config):
    video_id: str


def get_transcript(config: ExtractTranscriptConfig) -> Generator[str, None, None]:
    """Yields transcript text entry by entry."""
    transcript = YouTubeTranscriptApi.get_transcript(config.video_id)
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


config: ExtractTranscriptConfig = ExtractTranscriptConfig(video_id="LPZh9BOjkQs")

for text in stream_transcript_chunks(get_transcript(config)):
    if text:
        text = utils.sanitize_text(text)
        print(text)
        print("\n-------------------------------------------------------------\n")
