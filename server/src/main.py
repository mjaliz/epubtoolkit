import os
from fastapi import FastAPI, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils.utils import drop_extension
from utils.translator import translations
from epubtoolkit.epub import Epub

current_dir = os.path.dirname(os.path.realpath(__file__))
books_dir = os.path.join(current_dir, "..", "..", "books")
if not os.path.isdir(books_dir):
    os.makedirs(books_dir)

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={
        "status": False,
        "message": {"text": str(exc.detail)},
        "data": None
    })


@app.post("/extract_sentence")
async def extract_sentence(file: UploadFile):
    book_name = drop_extension(file.filename)
    book_base_dir = os.path.join(books_dir, book_name)
    try:
        os.makedirs(book_base_dir)
    except FileExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=translations.get("sentence_extracted_already"))
    book_dir = os.path.join(book_base_dir, file.filename)
    with open(book_dir, 'wb') as f:
        f.write(file.file.read())

    epub = Epub(book_dir)
    epub.sync_audio()

    return "ok"
