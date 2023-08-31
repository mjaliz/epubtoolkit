import pymongo
from typing import Optional, List
from pydantic import BaseModel
from beanie import Document, Indexed


class Sentence(BaseModel):
    text: str
    translation: str


class EpubBook(Document):
    file_name: str
    file_path: str
    book_name: Indexed(str)
    sentences: List[Sentence]

    class Settings:
        name = "books"
