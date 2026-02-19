from fastapi import HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.security import hash_password,verify_password
from app.core.jwt import create_access_token

router = APIRouter(
    prefix="/auth",
    tags= ["Auth"]
)

@router.post("/register",response_model=UserResponse)

def register(
    user: UserCreate,
    db : Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = hash_password(user.password)

    new_user = User(
        email = user.email,
        hashed_password = hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:                                                             #check for email
        raise HTTPException(status_code=400,detail="Invalid credentials")    #don't reveal which part failed due to security reasons
    
    if not verify_password(credentials.password,user.hashed_password):
        raise HTTPException(status_code=400,detail="Invalid credentials")
    
    access_token = create_access_token(
        data = {"sub":str(user.id)}
    )

    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }

