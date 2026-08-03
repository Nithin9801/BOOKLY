from typing import List
from uuid import UUID

from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.books.schemas import (BookResponse,
                                BookUpdateModel,
                                BookCreateModel,
                                BookRevTagResponse)
from src.db.main import get_session
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.errors import BookNotFound

from .service import BookService




book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["user","admin"]))

@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookResponse,dependencies=[role_checker])
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
) -> dict:
    user_uid = token_details.get('user')['user_uid']
    new_book = await book_service.create_book(book_data,user_uid, session)
    return new_book


@book_router.get("/", response_model=List[BookResponse])
async def get_all_books(
    session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)
):
    books = await book_service.get_all_books(session)
    return books

@book_router.get("/user/{user_uid}", response_model=List[BookResponse],dependencies=[role_checker])
async def get_all_user_books(
    user_uid:str,session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)
):
    books = await book_service.get_all_user_books(user_uid,session)
    return books



@book_router.get("/{book_uid}", response_model=BookRevTagResponse)
async def get_a_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
) -> dict:
    book = await book_service.get_book(book_uid, session)

    if book:
        return book
    else:
        raise BookNotFound()


@book_router.patch("/{book_uid}", response_model=BookResponse,dependencies=[role_checker])
async def update_book(
    book_uid: UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
) -> dict:
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    if updated_book:
        return updated_book
    else:
        raise BookNotFound()


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT,dependencies=[role_checker])
async def delete_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
):
    book_to_delete = await book_service.delete_book(book_uid, session)

    if book_to_delete:
        return book_to_delete
    else:
        raise BookNotFound()
