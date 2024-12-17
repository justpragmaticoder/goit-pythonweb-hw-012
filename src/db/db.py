import contextlib
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from src.conf.config import config

class DatabaseSessionManager:
    """
    A manager for handling asynchronous database sessions.

    This class provides a centralized way to manage database connections and sessions
    using SQLAlchemy's asynchronous engine and session maker.

    Attributes:
        _engine (AsyncEngine | None): The asynchronous SQLAlchemy engine.
        _session_maker (async_sessionmaker): The session maker bound to the engine.
    """

    def __init__(self, url: str):
        """
        Initialize the DatabaseSessionManager.

        Args:
            url (str): The database connection URL.

        Example:
            manager = DatabaseSessionManager("postgresql+asyncpg://user:password@localhost/dbname")
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provide an asynchronous context manager for a database session.

        This method yields an asynchronous SQLAlchemy session. It ensures that
        any SQLAlchemy exceptions are caught, the transaction is rolled back,
        and the session is closed properly after use.

        Yields:
            AsyncSession: An active database session.

        Raises:
            Exception: If the session maker is not initialized.
            SQLAlchemyError: If a database-related error occurs during the transaction.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


# Global instance of DatabaseSessionManager
sessionmanager = DatabaseSessionManager(config.DB_URL)
"""
Global instance of DatabaseSessionManager for managing database sessions.

This instance is configured using the database URL from the application settings.
"""


async def get_db():
    """
    Dependency for retrieving an asynchronous database session.

    This function provides a database session to FastAPI endpoints by using the
    global `sessionmanager`. It ensures that the session is properly opened and
    closed for each request.

    Yields:
        AsyncSession: A database session for use within a request context.
    """
    async with sessionmanager.session() as session:
        yield session