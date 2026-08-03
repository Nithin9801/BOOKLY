from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select,desc

from .schemas import BookCreateModel,BookUpdateModel

from src.db.models import BookDb



class BookService:
    async def get_all_books(self,session:AsyncSession) -> dict:
        statement = select(BookDb).order_by(desc(BookDb.created_at))

        result = await session.exec(statement)

        return result.all()

    async def get_all_user_books(self,user_uid:UUID,session:AsyncSession) -> dict:
            statement = select(BookDb).where(BookDb.user_uid == user_uid).order_by(desc(BookDb.created_at))
    
            result = await session.exec(statement)
    
            return result.all()

    async def get_book(self,book_uid:UUID,session:AsyncSession) -> dict:
        statement = select(BookDb).where(BookDb.uid == book_uid)
        result = await session.exec(statement)

        book = result.first()
        return book if book is not None else None
        
    async def create_book(self,book_data:BookCreateModel,user_uid:UUID,session:AsyncSession) -> dict:
        book_data_dic = book_data.model_dump()  

        new_book = BookDb(**book_data_dic) 
        new_book.user_uid = UUID(user_uid)
        
        session.add(new_book) 

        await session.commit() 
        await session.refresh(new_book)

        return new_book


    async def update_book(self,book_uid:UUID,book_data:BookUpdateModel,session:AsyncSession) -> dict:
        book_to_update = await self.get_book(book_uid,session)

        if book_to_update is not None:
            book_update_data = book_data.model_dump()

            for k,v in book_update_data.items():
                setattr(book_to_update,k,v)

            await session.commit()

            return book_to_update

        else:
            return None

        

    async def delete_book(self,book_uid:UUID,session:AsyncSession):
        book_to_delete = await self.get_book(book_uid,session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return {"message":"Deleted"}
        else:
            return None