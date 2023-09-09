import os
import shutil
from fastapi import FastAPI, UploadFile, HTTPException, status, Request, Query, Form, File
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import FileResponse
from tempfile import gettempdir

from .utils.utils import drop_extension
from .utils.translator import translations
from .epubtoolkit.epub import Epub
from .db.database import init
from .db.models import EpubBook

current_dir = os.path.dirname(os.path.realpath(__file__))
temp_dir = gettempdir()
# books_dir = os.path.join(current_dir, "..", "..", "books")
# translations_dir = os.path.join(books_dir, "translations")
books_dir = os.path.join(temp_dir, "books")
translations_dir = os.path.join(temp_dir, "books", "translations")
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


def upload_file(file: UploadFile, base_dir):
    book_name = drop_extension(file.filename)
    book_base_dir = os.path.join(base_dir, book_name)
    if os.path.isdir(book_base_dir):
        shutil.rmtree(book_base_dir)
    os.makedirs(book_base_dir)
    book_dir = os.path.join(book_base_dir, file.filename)
    with open(book_dir, 'wb') as f:
        f.write(file.file.read())
    return book_dir, book_base_dir


@app.post("/api/upload_book")
async def upload_book(book: EpubBook):
    await book.create()
    return {"status": "ok"}


@app.post("/api/extract_sentence")
async def extract_sentence(file: UploadFile):
    book_dir, book_base_dir = upload_file(file, books_dir)

    epub = Epub(book_dir)
    epub.extract_sentence()

    return JSONResponse(content={"data": book_base_dir}, status_code=status.HTTP_201_CREATED)


@app.get("/api/download_translations")
async def download(book_path: str):
    if not os.path.isdir(book_path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=translations.get("book_not_uploaded"))
    file_name = f'{book_path.split("/")[-1].replace(".epub", "")}_xlsxs.zip'
    file_path = os.path.join(book_path, file_name)
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return FileResponse(path=file_path, status_code=status.HTTP_200_OK, headers=headers, media_type='application/zip')


@app.post("/api/sync_audio")
async def extract_sentence(file: UploadFile = File(...), has_translation: bool = Form(...)):
    book_dir, book_base_dir = upload_file(file, books_dir)

    epub = Epub(book_dir)
    epub.sync_audio(has_translation)

    return JSONResponse(content={"data": book_base_dir}, status_code=status.HTTP_201_CREATED)


@app.get("/api/download_synced_audio")
async def download(book_path: str):
    if not os.path.isdir(book_path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=translations.get("book_not_uploaded"))
    file_name = f'{book_path.split("/")[-1]}_synced.epub'
    file_path = os.path.join(book_path, file_name)
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return FileResponse(path=file_path, status_code=status.HTTP_200_OK, headers=headers,
                        media_type='application/zip+epub')


@app.post("/api/sync_translation")
async def extract_sentence(book_file: UploadFile, translation_file: UploadFile):
    book_dir, book_base_dir = upload_file(book_file, books_dir)
    translation_dir, translation_base_dir = upload_file(
        translation_file, translations_dir)

    epub = Epub(book_dir)
    epub.sync_translation(translation_dir)

    return JSONResponse(content={"data": book_base_dir}, status_code=status.HTTP_201_CREATED)


@app.get("/api/download_synced_translation")
async def download(book_path: str):
    if not os.path.isdir(book_path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=translations.get("book_not_uploaded"))
    file_name = f'{book_path.split("/")[-1]}_t.epub'
    file_path = os.path.join(book_path, file_name)
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return FileResponse(path=file_path, status_code=status.HTTP_200_OK, headers=headers,
                        media_type='application/zip+epub')
