import logging
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from traceback import print_exception

from server.src.utils.translator import translations


class CatchExceptions(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logging.error(e)
            print_exception(e)
            return JSONResponse(status_code=500, content={
                "status": False,
                "message": {"text": translations.get("runtime_error")},
                "data": None
            })
