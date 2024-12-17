import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from src.schemas import ContactModel

# Mock user data
user_data = {
    "id": 1,
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "user",
    "confirmed": True,
}

# Mock contacts
contacts = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "birth_date": "1990-12-15",
        "email": "john.doe@example.com",
        "phone_number": "123-456-7890",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
    },
    {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Doe",
        "birth_date": "1995-12-20",
        "email": "jane.doe@example.com",
        "phone_number": "987-654-3210",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00",
    },
]

# Payload for creating/updating contacts
payload = {
    "first_name": "John",
    "last_name": "Doe",
    "birth_date": "1990-12-15",
    "email": "john.doe@example.com",
    "phone_number": "123-456-7890",
}


# @pytest.mark.asyncio
# async def test_get_upcoming_birthdays(client, monkeypatch, auth_headers):
#     """
#     Test retrieving contacts with upcoming birthdays.
#     """
#     # Mock dependencies
#     mock_get_user = AsyncMock(return_value=user_data)
#     monkeypatch.setattr("src.services.auth.get_current_user", mock_get_user)
# 
#     mock_get_birthdays = AsyncMock(return_value=contacts)
#     monkeypatch.setattr(
#         "src.services.contacts.ContactService.list_upcoming_birthdays",
#         mock_get_birthdays,
#     )
# 
#     # API request
#     response = client.get("/api/contacts/birthdays?days=7", headers=auth_headers)
# 
#     # Assertions
#     assert response.status_code == 200
#     assert len(response.json()) == len(contacts)
#     assert response.json()[0]["email"] == contacts[0]["email"]
#     mock_get_birthdays.assert_called_once_with(7)


@pytest.mark.asyncio
async def test_get_contact_not_found(client, monkeypatch, auth_headers):
    """
    Test retrieving a non-existent contact.
    """
    # Mock dependencies
    mock_get_user = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_user)

    mock_retrieve_contact = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "src.services.contacts.ContactService.retrieve_contact", mock_retrieve_contact
    )

    # API request
    response = client.get("/api/contacts/999", headers=auth_headers)

    # Assertions
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"
    mock_retrieve_contact.assert_called_once_with(999)


@pytest.mark.asyncio
async def test_delete_contact_not_found(client, monkeypatch, auth_headers):
    """
    Test deleting a non-existent contact.
    """
    # Mock dependencies
    mock_get_user = AsyncMock(return_value=user_data)
    monkeypatch.setattr("src.services.auth.get_current_user", mock_get_user)

    mock_delete_contact = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found.",
        )
    )
    monkeypatch.setattr(
        "src.services.contacts.ContactService.delete_contact", mock_delete_contact
    )

    contact_id = 999
    # API request
    response = client.delete(f"/api/contacts/{contact_id}", headers=auth_headers)

    # Assertions
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found."
    mock_delete_contact.assert_called_once_with(contact_id)