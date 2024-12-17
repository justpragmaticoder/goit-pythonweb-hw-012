from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """
    Configuration class for managing application settings.

    This class uses Pydantic's `BaseSettings` to parse and validate environment variables.
    It provides default values for some settings and supports reading from an `.env` file.

    Attributes:
        JWT_SECRET (str): Secret key for signing JWT tokens.
        JWT_ALGO (str): Algorithm used for signing JWT tokens. Default is `HS256`.
        JWT_EXPIRATION_SECONDS (int): Token expiration time in seconds. Default is `3600` (1 hour).

        DB_URL (str): Database connection URL for application runtime.
        ALEMBIC_DB_URL (str): Database connection URL for Alembic migrations.

        USE_CREDENTIALS (bool): Whether to use credentials for email sending. Default is `True`.
        VALIDATE_CERTS (bool): Whether to validate SSL/TLS certificates for email. Default is `True`.

        MAIL_USERNAME (EmailStr): Username for the email server.
        MAIL_PASSWORD (str): Password for the email server.
        MAIL_FROM (EmailStr): Sender's email address.
        MAIL_PORT (int): Port number for the email server.
        MAIL_SERVER (str): Hostname of the email server.
        MAIL_FROM_NAME (str): Default name to use as sender in emails. Default is `"Rest API Service"`.
        MAIL_STARTTLS (bool): Whether to enable STARTTLS for the email server. Default is `False`.
        MAIL_SSL_TLS (bool): Whether to enable SSL/TLS for the email server. Default is `True`.
        MAIL_TOKEN_EXP_DAYS (int): Number of days for email tokens to remain valid. Default is `7`.

        CLOUDINARY_NAME (str): Cloudinary account name.
        CLOUDINARY_API_KEY (int): Cloudinary API key.
        CLOUDINARY_API_SECRET (str): Cloudinary API secret.

        model_config (ConfigDict): Pydantic configuration for the settings model.
    """
    JWT_SECRET: str
    JWT_ALGO: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    DB_URL: str = f"postgresql+asyncpg://postgres:567234@postgres:5432/rest_app"
    ALEMBIC_DB_URL: str = f"postgresql+asyncpg://postgres:567234@localhost:5432/rest_app"

    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    MAIL_TOKEN_EXP_DAYS: int = 7

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Instantiate the configuration
config = Config()
"""
Global instance of the Config class.

This instance is used throughout the application to access configuration settings.
"""