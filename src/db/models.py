from sqlmodel import SQLModel,Field,Relationship
import sqlalchemy.dialects.mysql as my
from sqlalchemy import Column,DateTime
from datetime import datetime,date

from uuid import UUID,uuid4
from typing import Optional,List

class User(SQLModel,table=True):
    __tablename__ = "users"

    uid : UUID = Field(
            default_factory=uuid4,
            primary_key=True
    )
    username:str
    email:str
    first_name:str
    last_name:str
    role: str = Field(
    sa_column=Column(
        my.VARCHAR(20),
        nullable=False,
        default="USER"
    )
    )   
    password_hash:str = Field(exclude=True)
    is_verified:bool = Field(default=False)
    created_at:datetime = Field(sa_column=Column(DateTime,default=datetime.now))
    updated_at:datetime =  Field(sa_column=Column(DateTime,default=datetime.now,onupdate=datetime.now))
    books: List["BookDb"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: List["Review"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"<User {self.username}>"

class Review(SQLModel,table=True):
    __tablename__ = "reviews"
    uid : UUID = Field(
        default_factory=uuid4,
        primary_key=True
    )
    rating : int = Field(lt=5)
    review_text : str
    created_at : datetime = Field(sa_column=Column(DateTime,default=datetime.now))
    updated_at : datetime = Field(sa_column=Column(DateTime,default=datetime.now,onupdate=datetime.now))
    user_uid : Optional[UUID] = Field(default=None,foreign_key="users.uid")
    book_uid : Optional[UUID] = Field(default=None,foreign_key="books.uid")
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["BookDb"] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review of book {self.book_uid} by the user {self.user_uid}>"   


class BookTag(SQLModel,table=True):
    book_uid:UUID = Field(default=None,foreign_key="books.uid",primary_key=True)
    tag_uid:UUID = Field(default=None,foreign_key="tags.uid",primary_key=True)

class BookDb(SQLModel,table=True):
    __tablename__ = "books"
    uid : UUID = Field(
        default_factory=uuid4,
        primary_key=True
    )
    title : str
    author : str
    publisher : str
    published_date : date
    page_count : int 
    language : str
    user_uid : Optional[UUID] = Field(default=None,foreign_key="users.uid")
    created_at : datetime = Field(sa_column=Column(DateTime,default=datetime.now))
    updated_at : datetime = Field(sa_column=Column(DateTime,default=datetime.now,onupdate=datetime.now))
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})
    tags: List["Tag"] = Relationship(link_model=BookTag,back_populates="books",sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"<Book {self.title}>"

class Tag(SQLModel,table = True):
    __tablename__ = "tags"

    uid : UUID = Field(
            default_factory=uuid4,
            primary_key=True,
            nullable=False
        )
    name:str = Field(
    sa_column=Column(
        my.VARCHAR(20),
        nullable=False
    )
    )
    created_at : datetime = Field(sa_column=Column(DateTime,default=datetime.now))
    books: List["BookDb"] = Relationship(
        link_model=BookTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"}
    )


    def __repr__(self) -> str:
        return f"<Tag {self.name}>"