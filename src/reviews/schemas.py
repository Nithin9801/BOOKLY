from pydantic import BaseModel
from sqlmodel import Field
from uuid import UUID
from datetime import datetime


class ReviewResponseModel(BaseModel):
    uid : UUID
    rating : int = Field(lt=5)
    review_text : str
    user_uid : UUID 
    book_uid : UUID 
    created_at : datetime 
    updated_at : datetime 

class ReviewCreateModel(BaseModel):
    rating : int = Field(lt=5)
    review_text : str
