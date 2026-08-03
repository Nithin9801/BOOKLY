from pydantic import BaseModel,Field
from uuid import UUID
from datetime import datetime
from src.books.schemas import BookResponse
from src.reviews.schemas import ReviewResponseModel
from typing import List

class UserCreateModel(BaseModel):
    username:str = Field(max_length=8)
    first_name:str = Field(max_length=8)
    last_name:str = Field(max_length=4)
    email:str = Field(max_length=40)
    password_hash:str = Field(min_length=6)

class UserResponse(BaseModel):
    uid : UUID 
    username:str
    email:str
    first_name:str
    last_name:str
    role:str
    password_hash:str = Field(exclude=True)
    is_verified:bool 
    created_at:datetime 
    updated_at:datetime 


class UserBookResponse(UserResponse):
    books: List[BookResponse]
    reviews : List[ReviewResponseModel]

class UserLoginModel(BaseModel):
    email:str
    password:str 

class EmailModel(BaseModel):
    adresses:List[str]

class PasswordResetRequestModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str