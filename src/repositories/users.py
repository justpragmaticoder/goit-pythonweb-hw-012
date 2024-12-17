from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    Repository class for managing user-related database operations.

    This class provides methods for querying, creating, and updating users in the database.

    Attributes:
        db (AsyncSession): The database session used for executing queries.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository with a database session.

        Args:
            session (AsyncSession): The asynchronous database session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user object if found, or `None` if no user exists with the given ID.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User | None: The user object if found, or `None` if no user exists with the given username.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The user object if found, or `None` if no user exists with the given email address.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user.

        Args:
            body (UserCreate): The data for the new user.
            avatar (str, optional): The URL of the user's avatar. Defaults to `None`.

        Returns:
            User: The newly created user object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirm_email(self, email: str) -> None:
        """
        Confirm a user's email address.

        Args:
            email (str): The email address to confirm.

        Returns:
            None
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL for a user.

        Args:
            email (str): The email address of the user whose avatar is to be updated.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object with the new avatar URL.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user