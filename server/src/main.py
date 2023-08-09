import os
import shutil
from fastapi import FastAPI, UploadFile, HTTPException, status, Request, Query
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import FileResponse

from .utils.utils import drop_extension
from .utils.translator import translations
from .epubtoolkit.epub import Epub

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


def upload_file(file: UploadFile):
    book_name = drop_extension(file.filename)
    book_base_dir = os.path.join(books_dir, book_name)
    if os.path.isdir(book_base_dir):
        shutil.rmtree(book_base_dir)
    os.makedirs(book_base_dir)
    book_dir = os.path.join(book_base_dir, file.filename)
    with open(book_dir, 'wb') as f:
        f.write(file.file.read())
    return book_dir, book_base_dir


@app.post("/extract_sentence")
async def extract_sentence(file: UploadFile):
    book_dir, book_base_dir = upload_file(file)

    epub = Epub(book_dir)
    epub.extract_sentence()

    return JSONResponse(content={"data": book_base_dir}, status_code=status.HTTP_201_CREATED)


@app.get("/download_translations")
async def download(book_path: str):
    if not os.path.isdir(book_path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=translations.get("book_not_uploaded"))
    file_name = f'{book_path.split("/")[-1].replace(".epub", "")}_csvs.zip'
    file_path = os.path.join(book_path, file_name)
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return FileResponse(path=file_path, status_code=status.HTTP_200_OK, headers=headers, media_type='application/zip')


@app.post("/sync_audio")
async def extract_sentence(file: UploadFile):
    book_dir, book_base_dir = upload_file(file)

    epub = Epub(book_dir)
    epub.sync_audio()

    return JSONResponse(content={"data": book_base_dir}, status_code=status.HTTP_201_CREATED)


@app.get("/download_synced_epub")
async def download(book_path: str):
    if not os.path.isdir(book_path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=translations.get("book_not_uploaded"))
    file_name = f'{book_path.split("/")[-1]}_synced.epub'
    file_path = os.path.join(book_path, file_name)
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return FileResponse(path=file_path, status_code=status.HTTP_200_OK, headers=headers,
                        media_type='application/zip+epub')
