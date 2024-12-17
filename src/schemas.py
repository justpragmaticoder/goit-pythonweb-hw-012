from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

class ContactModel(BaseModel):
    """
    Represents the base model for a contact.

    Attributes:
        first_name (str): The first name of the contact. Must be between 2 and 50 characters.
        last_name (str): The last name of the contact. Must be between 2 and 50 characters.
        email (EmailStr): The email address of the contact. Must be between 7 and 80 characters.
        phone_number (str): The phone number of the contact. Must be between 7 and 15 characters.
        birthday_date (date): The birth date of the contact.
        info (Optional[str]): Additional information about the contact. Default is None.
    """
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(min_length=7, max_length=80)
    phone_number: str = Field(min_length=7, max_length=15)
    birthday_date: date
    info: Optional[str] = None

class ContactResponse(ContactModel):
    """
    Represents the response model for a contact, extending `ContactModel`.

    Attributes:
        id (int): The unique identifier of the contact.
        created_at (datetime): The timestamp when the contact was created.
        updated_at (Optional[datetime]): The timestamp when the contact was last updated. Default is None.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    """
    Represents the user model for API responses.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        avatar (str): The URL of the user's avatar.
    """
    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    """
    Represents the model for creating a new user.

    Attributes:
        username (str): The username of the new user.
        email (str): The email address of the new user.
        password (str): The password of the new user.
    """
    username: str
    email: str
    password: str

class Token(BaseModel):
    """
    Represents a model for authentication tokens.

    Attributes:
        access_token (str): The access token for the user.
        token_type (str): The type of the token (e.g., "bearer").
    """
    access_token: str
    token_type: str

class RequestEmail(BaseModel):
    """
    Represents a model for requesting email verification or other email-related operations.

    Attributes:
        email (EmailStr): The email address for the request.
    """
    email: EmailStr
    
    
class ResetPassword(BaseModel):
    """
    Reset password model for resetting user password

    Attributes:
        email (str): Email of the user
        password (str): Password of the user
    """

    email: EmailStr
    password: str = Field(min_length=4, max_length=128, description="New Password")