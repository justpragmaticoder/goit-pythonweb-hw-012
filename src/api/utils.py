from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.db.db import get_db

router = APIRouter(tags=["utils"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    """
    Perform a health check for the application and database.

    This endpoint verifies the connection to the database by executing a simple query.
    If the database is properly configured and accessible, it returns a success message.
    Otherwise, it raises an HTTP exception indicating an issue.

    Args:
        db (AsyncSession): The database session, injected as a dependency.

    Returns:
        dict: A message indicating the application status (e.g., `{"message": "Welcome to FastAPI!"}`).

    Raises:
        HTTPException: If there is an issue connecting to the database or if the database is misconfigured.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the db",
        )