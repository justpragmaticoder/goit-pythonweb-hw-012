from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail, ResetPassword
from src.services.email import send_email_confirmation, send_reset_password_email
from src.services.auth import create_access_token, Hash, get_email_from_token, get_password_from_token
from src.services.users import UserService
from src.db.db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    background_tasks: BackgroundTasks,
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.

    This endpoint creates a new user with the provided credentials and sends a confirmation email.

    Args:
        user_data (UserCreate): Data for creating a new user.
        background_tasks (BackgroundTasks): Background tasks manager for sending emails.
        request (Request): The current request object to construct the base URL.
        db (AsyncSession): The database session.

    Returns:
        User: The created user object.

    Raises:
        HTTPException: If the email or username is already in use.
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You can't use this email",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You can't use this username",
        )
    user_data.password = Hash().get_pwd_hash(user_data.password)
    new_user = await user_service.create_user(user_data)
    background_tasks.add_task(
        send_email_confirmation, new_user.email, new_user.username, str(request.base_url)
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    """
    Log in a user.

    This endpoint authenticates the user using their username and password and returns an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The form containing username and password.
        db (AsyncSession): The database session.

    Returns:
        Token: An access token for the authenticated user.

    Raises:
        HTTPException: If credentials are incorrect or the email is not confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed",
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm a user's email.

    This endpoint verifies the email confirmation token and updates the user's email status.

    Args:
        token (str): The email confirmation token.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the email confirmation status.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email is already confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request email verification.

    This endpoint sends an email verification request to the user.

    Args:
        body (RequestEmail): The request body containing the email address.
        background_tasks (BackgroundTasks): Background tasks manager for sending emails.
        request (Request): The current request object to construct the base URL.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the email verification status.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email_confirmation, user.email, user.username, str(request.base_url)
        )
    return {"message": "Check your mail for verification"}

@router.post("/reset_password")
async def reset_password_request(
    body: ResetPassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Requests to reset a user's password.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        # DO not notify that user exists
        return {"message": "Check your email"}

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not confirmed",
        )

    hashed_password = Hash().get_password_hash(body.password)

    reset_token = await create_access_token(
        data={"sub": user.email, "password": hashed_password}
    )

    # Send email
    background_tasks.add_task(
        send_reset_password_email,
        to_email=body.email,
        username=user.username,
        host=str(request.base_url),
        reset_token=reset_token,
    )

    return {"message": "Check your email"}


@router.get("/confirm_reset_password/{token}")
async def confirm_reset_password(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirms reset a user's password.
    """
    email = await get_email_from_token(token)
    hashed_password = await get_password_from_token(token)

    if not email or not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update password
    await user.reset_password(user.id, hashed_password)

    return {"message": "Password successfully changed"}

