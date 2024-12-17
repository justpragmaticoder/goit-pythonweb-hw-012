import logging
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import config

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure email connection
conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_STARTTLS=config.MAIL_STARTTLS,
    MAIL_SSL_TLS=config.MAIL_SSL_TLS,
    USE_CREDENTIALS=config.USE_CREDENTIALS,
    VALIDATE_CERTS=config.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "mail-templates",
)
"""
Global email configuration for FastMail.

This configuration is used to send emails with the specified settings, such as 
email server, port, authentication, and template folder.
"""


async def send_reset_password_email(
    to_email: EmailStr, username: str, host: str, reset_token: str
) -> None:
    """
    Send a reset password email to the user.

    Args:
        to_email (EmailStr): Email of the user.
        username (str): Username of the user.
        host (str): Host of the server.
        reset_token (str): Reset token of the user.

    Returns:
        None

    Raises:
        ConnectionErrors: If there is an error sending the email.
    """
    try:
        reset_link = f"{host}api/auth/confirm_reset_password/{reset_token}"

        message = MessageSchema(
            subject="Important: Update your account information",
            recipients=[to_email],
            template_body={"reset_link": reset_link, "username": username},
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        logger.error("A connection error occurred: %s", err)


async def send_email_confirmation(email: EmailStr, username: str, host: str) -> None:
    """
    Send an email to a user for email verification.

    This function creates a verification token, formats an email message using a 
    template, and sends the email to the specified recipient.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The recipient's username to personalize the email.
        host (str): The host URL for generating the verification link.

    Returns:
        None

    Raises:
        ConnectionErrors: If there is an error connecting to the email server.
    """
    try:
        # Generate the email verification token
        token_verification = create_email_token({"sub": email})

        # Define the email message
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        logger.error("A connection error occurred: %s", err)