import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status
from src.services.auth import create_access_token

# Constants
UNAUTHORIZED = "Not authenticated"

# Test user data
user_data_admin = {
    "id": 1,
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
    "role": "admin",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}

user_data_not_admin = {
    "id": 2,
    "username": "agent008",
    "email": "agent008@gmail.com",
    "password": "12345678",
    "role": "user",
    "confirmed": True,
    "avatar": "https://example.com/avatar.png",
}


@pytest.fixture
def auth_headers():
    """
    Fixture to provide valid Authorization headers.
    """
    valid_token = create_access_token({"sub": user_data_admin["username"]})
    return {"Authorization": f"Bearer {valid_token}"}


# @pytest.mark.asyncio
# async def test_me(client, monkeypatch, auth_headers):
#     """
#     Test successful retrieval of current user data.
#     """
#     # Mock JWT decode
#     mock_jwt_decode = MagicMock(return_value={"sub": user_data_admin["username"]})
#     monkeypatch.setattr("jose.jwt.decode", mock_jwt_decode)
# 
#     # Mock UserService to return the user
#     mock_user_service = AsyncMock()
#     mock_user_service.get_user_by_username = AsyncMock(return_value=user_data_admin)
#     monkeypatch.setattr("src.services.users.UserService", lambda db: mock_user_service)
# 
#     # Debugging
#     print("Authorization Header:", auth_headers)
# 
#     # API call to retrieve current user
#     response = client.get("/api/users/me", headers=auth_headers)
# 
#     # Debugging
#     print("Response Status Code:", response.status_code)
#     print("Response JSON:", response.json())
# 
#     # Assertions
#     assert response.status_code == 200
#     assert response.json()["email"] == user_data_admin["email"]
#     assert response.json()["username"] == user_data_admin["username"]
# 
#     # Ensure mocks were called
#     mock_jwt_decode.assert_called_once()
#     mock_user_service.get_user_by_username.assert_called_once_with(
#         user_data_admin["username"]
#     )


@pytest.mark.asyncio
async def test_me_unauthenticated(client, monkeypatch):
    """
    Test unauthorized access when retrieving current user data.
    """
    # Mock get_current_user to raise HTTPException
    mock_get_current_user = AsyncMock(
        side_effect=HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=UNAUTHORIZED
        )
    )
    monkeypatch.setattr(
        "src.services.auth.get_current_user", mock_get_current_user
    )

    # API call to retrieve current user without authorization
    response = client.get("/api/users/me")

    # Assertions
    assert response.status_code == 401
    assert response.json()["detail"] == UNAUTHORIZED