from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,desc

from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from .schemas import ReviewCreateModel
from uuid import UUID

import logging



book_service = BookService()
user_service = UserService()


class ReviewService:

    async def add_review_to_book(self,user_email:str,book_uid:UUID,review_data:ReviewCreateModel,session:AsyncSession):
        try:
            book = await book_service.get_book(book_uid = book_uid,session = session)
            user = await user_service.get_user_by_email(email = user_email,session = session)

            review_data = review_data.model_dump()

            new_review_data = Review(**review_data)

            new_review_data.user = user
            new_review_data.book = book 

            session.add(new_review_data)
            await session.commit()

            return new_review_data

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OOPs... something went wrong"
            )


    async def get_all_reviews(self,session:AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)

        return result.all()


    async def get_review(self,review_uid:UUID,session:AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)

        result = await session.exec(statement)

        return result.first()

    async def delete_review_to_from_book(self,review_uid:UUID,user_email:str,session:AsyncSession):
        user = await user_service.get_user_by_email(user_email,session)

        review = self.get_review(review_uid,session)

        if not review or (review.user is not user):
            raise HTTPException(
                detail="Cannot delete this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        session.add(review)

        await session.commit()
