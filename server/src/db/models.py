import pymongo
from typing import Optional
from pydantic import BaseModel
from beanie import Document, Indexed


class Sentence(BaseModel):
    text: str
    translation: str


class SentenceFid(BaseModel):
    fid: Sentence


class EpubBook(Document):
    file_name: str
    file_path: str
    book_name: Indexed(str)
    sentence: SentenceFid

    class Settings:
        name = "books"
