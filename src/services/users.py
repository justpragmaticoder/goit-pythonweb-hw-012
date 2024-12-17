import logging

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repositories.users import UserRepository
from src.schemas import UserCreate

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for managing user-related operations.

    This class provides an interface for performing user-related tasks, such as
    creating a user, retrieving user details, updating avatars, and confirming emails.

    Attributes:
        repository (UserRepository): An instance of the user repository for database interactions.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.

        Args:
            db (AsyncSession): The asynchronous database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user.

        This method attempts to retrieve a Gravatar image for the user's email address
        and uses it as the default avatar. If an error occurs, the avatar will be set to `None`.

        Args:
            body (UserCreate): The user creation data.

        Returns:
            User: The newly created user object.
        """
        avatar = None
        try:
            gravatar_inst = Gravatar(body.email)
            avatar = gravatar_inst.get_image()
        except Exception as e:
            logger.error("Create user exception occurred: %s", e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User | None: The user object if found, or `None` if no user exists with the given username.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            User | None: The user object if found, or `None` if no user exists with the given ID.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            User | None: The user object if found, or `None` if no user exists with the given email address.
        """
        return await self.repository.get_user_by_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update the avatar URL for a user.

        Args:
            email (str): The email address of the user whose avatar URL is to be updated.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object.
        """
        return await self.repository.update_avatar_url(email, url)

    async def confirmed_email(self, email: str):
        """
        Confirm a user's email address.

        Args:
            email (str): The email address to confirm.

        Returns:
            None
        """
        return await self.repository.confirm_email(email)