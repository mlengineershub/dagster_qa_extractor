from pydantic import BaseModel


class Entry(BaseModel):
    question: str
    answer: str


class ListEntries(BaseModel):
    entries: list[Entry]
