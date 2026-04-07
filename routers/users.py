from fastapi import APIRouter

from models import UserCreate

router = APIRouter(tags=["3.1 Users"])


@router.post("/create_user")
def create_user(user: UserCreate):
    return user
