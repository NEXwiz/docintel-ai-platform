import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

def save_uploaded_file(file : UploadFile, user_id: int) -> str:
    user_dir = os.path.join(UPLOAD_DIR, f"user_{user_id}")
    os.makedirs(user_dir,exist_ok=True)                 #doesnt make new directories for the same users

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(user_dir,unique_name)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path