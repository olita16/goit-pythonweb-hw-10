from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from src.repository.user import update_avatar_url
from src.services.upload_file import UploadFileService
from src.schemas.auth import User
from src.db.models import User as UserORM
from src.db.connect import get_db

from src.services.auth import auth_service
from src.settings.config import settings


router = APIRouter(prefix="/user", tags=["users"])


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
    file: UploadFile = File(),
    user: UserORM = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    avatar_url = UploadFileService(
        settings.CLOUDINARY_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ).upload_file(file, user.email)

    await update_avatar_url(user.email, avatar_url, db)
    user.avatar = avatar_url
    return user