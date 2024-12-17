from enum import Enum
from datetime import datetime, date
from sqlalchemy import Integer, String, func, Column, ForeignKey, Boolean, Enum as SqlEnum
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.sqltypes import DateTime, Date


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    This class serves as a foundation for defining models using SQLAlchemy's Declarative system.
    """
    pass

class Role(str, Enum):
    """
    Enum for user roles
    """

    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    Model representing a contact in the database.

    Attributes:
        id (int): Primary key, unique identifier for each contact.
        first_name (str): First name of the contact. Required, max length 50.
        last_name (str): Last name of the contact. Required, max length 50.
        email (str): Email address of the contact. Must be unique. Required, max length 80.
        phone_number (str): Phone number of the contact. Must be unique. Required, max length 15.
        birthday_date (date): Birthday of the contact. Required.
        created_at (datetime): Timestamp of when the contact was created. Auto-generated.
        updated_at (datetime): Timestamp of the last update. Auto-generated on update.
        info (str): Additional information about the contact. Optional, max length 500.
    """
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    birthday_date: Mapped[date] = mapped_column("birthday_date", Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        "updated_at", DateTime, default=func.now(), onupdate=func.now()
    )
    info: Mapped[str] = mapped_column(String(500), nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", backref="contacts")


class User(Base):
    """
    Model representing a user in the database.

    Attributes:
        id (int): Primary key, unique identifier for each user.
        username (str): Username of the user. Must be unique. Required.
        email (str): Email address of the user. Must be unique. Required.
        hashed_password (str): Hashed password for the user. Required.
        created_at (datetime): Timestamp of when the user was created. Auto-generated.
        avatar (str): URL of the user's avatar. Optional, max length 255.
        confirmed (bool): Status indicating whether the user's email is confirmed. Default is False.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[Role] = mapped_column(SqlEnum(Role), default=Role.USER, nullable=False)