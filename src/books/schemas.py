from pydantic import BaseModel
from datetime import datetime,date
from uuid import UUID
from typing import List
from src.reviews.schemas import ReviewResponseModel
from src.Tags.schemas import TagModel



class BookResponse(BaseModel):
    uid : UUID
    title : str
    author : str
    publisher : str
    published_date : date
    page_count : int 
    language : str
    created_at : datetime
    updated_at : datetime

class BookRevTagResponse(BookResponse):
    reviews: List[ReviewResponseModel]
    tags: List[TagModel]
    


class BookCreateModel(BaseModel):
    title : str
    author : str
    publisher : str
    published_date : date
    page_count : int 
    language : str

class BookUpdateModel(BaseModel):
    title : str
    author : str
    publisher : str
    page_count : int 
    language : str