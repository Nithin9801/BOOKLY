from fastapi import FastAPI

from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.Tags.routes import tag_router
from src.middleware import register_middleware

from .errors import register_error_handlers



version = "v1"
app = FastAPI(
    title="Bookly",
    description="A REST API for book description web service",
    version=version
)

register_error_handlers(app)

register_middleware(app)

app.include_router(book_router,prefix=f"/api/{version}/books", tags=['books'])
app.include_router(auth_router,prefix=f"/api/{version}/user", tags=['auth'])
app.include_router(review_router,prefix=f"/api/{version}/review", tags=['reviews'])
app.include_router(tag_router,prefix=f"/api/{version}/tags", tags=['tags'])