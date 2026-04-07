from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from config import ACCEPT_LANGUAGE_RE


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_subscribed: Optional[bool] = None

    @field_validator("age")
    @classmethod
    def age_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("age must be a positive integer")
        return v


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


class LoginData(BaseModel):
    username: str
    password: str


class CommonHeaders(BaseModel):
    user_agent: str
    accept_language: str

    model_config = {"populate_by_name": True}

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v):
        if not ACCEPT_LANGUAGE_RE.match(v):
            raise ValueError("Invalid Accept-Language format")
        return v
