from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt

def decode_access_token(token:str) -> dict:
    try:
        payload = jwt.decode(                  #positive selection, never negative comparison.(explicitly allowed)
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]              #list here because hackers might try to change the algo
        )
        return payload
    except JWTError:
        return None