from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate,UserResponse
from app.core.deps import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/",response_model=UserResponse)
def create_user(
    user:UserCreate,
    db: Session = Depends(get_db)
):
    new_user = User(
        email = user.email,
        hashed_password = user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/",response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/me",response_model=UserResponse)
def get_me(
    current_user : User = Depends(get_current_user)
):
    return current_user   