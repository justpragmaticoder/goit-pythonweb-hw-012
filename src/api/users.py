from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.db.db import get_db
from src.schemas import User
from src.services.auth import get_current_user, get_admin_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=User, description="No more than 10 requests per minute")
@limiter.limit("10 per minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user's profile.

    Args:
        request (Request): The incoming HTTP request.
        user (User): The authenticated user, injected via the `get_current_user` dependency.

    Returns:
        User: The profile of the currently authenticated user.

    Note:
        This endpoint is rate-limited to 10 requests per minute.
    """
    return user


@router.patch("/avatar", response_model=User)
async def update_avatar_user(
        file: UploadFile = File(),
        user: User = Depends(get_admin_user),
        db: AsyncSession = Depends(get_db),
):
    """
    Update the authenticated user's avatar.

    This endpoint allows the user to upload a new avatar image, which is stored in a cloud storage
    (e.g., Cloudinary), and updates the user's profile with the new avatar URL.

    Args:
        file (UploadFile): The avatar image file to upload.
        user (User): The authenticated user, injected via the `get_current_user` dependency.
        db (AsyncSession): The database session.

    Returns:
        User: The updated user profile with the new avatar URL.

    Raises:
        HTTPException: If an error occurs during file upload or database update.
    """
    avatar_url = UploadFileService(
        config.CLOUDINARY_NAME, config.CLOUDINARY_API_KEY, config.CLOUDINARY_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user