from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

import time
import sys
import logging

logger = logging.getLogger("uvicorn.access")
logger.disabled = True

class ColoredFormatter(logging.Formatter):
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[31m"
    RESET = "\x1b[0m"

    FORMAT_STRING = "%(levelname)s %(message)s"

    FORMATS = {
        logging.INFO: GREEN + FORMAT_STRING + RESET,
        logging.WARNING: YELLOW + FORMAT_STRING + RESET,
        logging.ERROR: RED + FORMAT_STRING + RESET,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT_STRING)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_custom_logger(name: str = "bookly_logger") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
    
        console_handler.setFormatter(ColoredFormatter())
        
        logger.addHandler(console_handler)

    return logger

cu_logger = setup_custom_logger()


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)
        processing_time = time.time() - start_time

        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time}s"

        if response.status_code >= 500:
            cu_logger.error(message)

        elif response.status_code >= 400:
            cu_logger.warning(message)

        else:
            cu_logger.info(message)

        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
