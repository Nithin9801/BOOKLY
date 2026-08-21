from fastapi import FastAPI

from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.Tags.routes import tag_router

from .middleware import register_middleware
from .errors import register_error_handlers



version = "v1"
version_prefix = "/api/{version}"

description = """
A REST API for a book review web service.

This REST API is able to;
- Create Read Update And delete books
- Add reviews to books
- Add tags to Books e.t.c.
    """


app = FastAPI(
    title="Bookly",
    description="A REST API for book description web service",
    version=version,
    contact={
        "name": "Nithin P",
        "email": "parmeshasp52@gmail.com",
    },
    terms_of_service="httpS://example.com/tos",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

register_error_handlers(app)

register_middleware(app)

app.include_router(book_router,prefix=f"/api/{version}/books", tags=['books'])
app.include_router(auth_router,prefix=f"/api/{version}/user", tags=['auth'])
app.include_router(review_router,prefix=f"/api/{version}/review", tags=['reviews'])
app.include_router(tag_router,prefix=f"/api/{version}/tags", tags=['tags'])