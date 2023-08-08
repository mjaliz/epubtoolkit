import os
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
    epub.extract_sentence()

    return {"data": book_base_dir}


@app.get("/download")
async def download(book_path: str):
    file_name = f'{book_path.split("/")[-1].replace(".epub", "")}_csvs.zip'
    file_path = os.path.join(book_path, file_name)
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return FileResponse(path=file_path, status_code=status.HTTP_200_OK, headers=headers, media_type='application/zip')
